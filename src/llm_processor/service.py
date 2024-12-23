"""Service for processing property listings using LLM."""
import json
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import MessageGroup, CleanedListing, MediaItem
from src.database.engine import async_session
from .processor import LLMProcessor
from .config import LLMConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ListingProcessorService:
    """Service for processing property listings."""
    
    def __init__(self, llm_processor: LLMProcessor):
        """Initialize the service."""
        self.llm_processor = llm_processor
        
    async def get_next_unprocessed(self, session: AsyncSession) -> Optional[MessageGroup]:
        """Get next unprocessed message group."""
        query = select(MessageGroup).outerjoin(
            CleanedListing
        ).where(
            CleanedListing.id == None
        ).limit(1)
        
        result = await session.execute(query)
        return result.scalar_one_or_none()
        
    async def process_listing(self, session: AsyncSession, group: MessageGroup, max_retries: int = 3) -> bool:
        """Process a single listing with retries.
        
        Returns:
            bool: True if processing was successful, False otherwise
        """
        for attempt in range(max_retries):
            try:
                # Get all messages
                messages = sorted(group.messages, key=lambda m: m.message_id)
                if not messages:
                    logger.warning(f"No messages found in group {group.id}")
                    return False
                    
                # Get the combined text
                combined_text = group.combined_text or " ".join(m.text for m in messages)
                
                # Get all image URLs
                media_items = [item for item in group.media_items if item.media_type == 'photo']
                image_urls = [item.file_url for item in media_items if item.file_url]
                
                # Process the listing
                property_details = await self.llm_processor.process_listing(combined_text)
                
                if property_details:
                    # Create new cleaned listing
                    cleaned_listing = CleanedListing(
                        group_id=group.id,
                        original_text=combined_text,
                        layout=property_details.layout.value,
                        area_sqm=property_details.area_sqm,
                        floor=property_details.floor,
                        total_floors=property_details.total_floors,
                        bedrooms=property_details.bedrooms,
                        has_balcony=property_details.has_balcony,
                        address=property_details.address,
                        district=property_details.district,
                        nearby_landmarks=json.dumps(property_details.nearby_landmarks) if property_details.nearby_landmarks else None,
                        monthly_rent_usd=property_details.monthly_rent_usd,
                        summer_rent_usd=property_details.summer_rent_usd,
                        requires_first_last=property_details.requires_first_last,
                        deposit_amount_usd=property_details.deposit_amount_usd,
                        commission=property_details.commission,
                        heating_type=property_details.heating_type.value if property_details.heating_type else None,
                        has_oven=property_details.has_oven,
                        has_microwave=property_details.has_microwave,
                        has_ac=property_details.has_ac,
                        has_internet=property_details.has_internet,
                        has_tv=property_details.has_tv,
                        has_parking=property_details.has_parking,
                        has_bathtub=property_details.has_bathtub,
                        is_furnished=property_details.is_furnished,
                        phone_numbers=json.dumps(property_details.phone_numbers),
                        whatsapp=property_details.whatsapp,
                        telegram=property_details.telegram,
                        contact_name=property_details.contact_name,
                        min_lease_months=property_details.min_lease_months,
                        max_lease_months=property_details.max_lease_months,
                        pet_policy=property_details.pet_policy.value if property_details.pet_policy else None,
                        has_contract=property_details.has_contract,
                        image_urls=json.dumps([url.hex() if isinstance(url, bytes) else str(url) for url in image_urls]),
                        processed_date=datetime.now(timezone.utc)
                    )
                    
                    session.add(cleaned_listing)
                    await session.commit()
                    logger.info(f"Successfully processed group {group.id}")
                    return True
                    
            except Exception as e:
                await session.rollback()
                if attempt < max_retries - 1:
                    logger.warning(f"Failed to process group {group.id} (attempt {attempt + 1}/{max_retries}): {str(e)}")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to process group {group.id} after {max_retries} attempts: {str(e)}")
                    
        return False

async def run_service(total_limit: int = 10, sleep_interval: int = 60):
    """Run the service continuously.
    
    Args:
        total_limit: Total number of items to process before stopping
        sleep_interval: Seconds to sleep when no items to process
    """
    config = LLMConfig()
    processor = LLMProcessor(config)
    service = ListingProcessorService(processor)
    
    processed_count = 0
    
    while processed_count < total_limit:
        try:
            async with async_session() as session:
                group = await service.get_next_unprocessed(session)
                
                if group:
                    logger.info(f"Processing group {group.id} ({processed_count + 1}/{total_limit})")
                    if await service.process_listing(session, group):
                        processed_count += 1
                else:
                    logger.info("No unprocessed listings found, sleeping...")
                    await asyncio.sleep(sleep_interval)
                    
        except Exception as e:
            logger.error(f"Service error: {str(e)}")
            await asyncio.sleep(sleep_interval)
            
    logger.info(f"Reached total limit of {total_limit} processed items. Stopping service.")

if __name__ == "__main__":
    asyncio.run(run_service(total_limit=10))
