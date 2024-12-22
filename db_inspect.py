#!/usr/bin/env python3
from sqlalchemy import func
from src.database.engine import get_db
from src.database.models import MessageGroup, Message, MediaItem, ChannelState
from tabulate import tabulate

def print_table(rows, headers):
    """Print data in a nice table format."""
    print(tabulate(rows, headers=headers, tablefmt='grid'))

def inspect_db():
    db = next(get_db())
    
    # Check Channel States
    print("\n=== Channel States ===")
    channel_states = db.query(ChannelState).all()
    if channel_states:
        rows = [(cs.channel_name, cs.last_message_id, cs.last_parsed_date) 
                for cs in channel_states]
        print_table(rows, ['Channel', 'Last Message ID', 'Last Parsed'])
    else:
        print("No channel states found")

    # Check Message Groups with Media
    print("\n=== Message Groups with Media ===")
    groups_with_media = (
        db.query(MessageGroup)
        .join(MediaItem)
        .order_by(MessageGroup.parsed_date.desc())
        .limit(5)
        .all()
    )
    
    if groups_with_media:
        rows = []
        for g in groups_with_media:
            media_items = db.query(MediaItem).filter(MediaItem.group_id == g.id).all()
            media_summary = {}
            for m in media_items:
                media_summary[m.media_type] = media_summary.get(m.media_type, 0) + 1
            
            media_info = [f"{type}: {count}" for type, count in media_summary.items()]
            rows.append([
                g.channel_name,
                g.group_id,
                g.combined_text[:50] + '...' if len(g.combined_text) > 50 else g.combined_text,
                g.posted_date,
                len(media_items),
                ', '.join(media_info)
            ])
        print_table(rows, ['Channel', 'Group ID', 'Text Preview', 'Posted Date', 'Media Count', 'Media Types'])
        
        # Get total counts
        total_groups = db.query(func.count(MessageGroup.id)).join(MediaItem).group_by(MessageGroup.id).count()
        total_media = db.query(func.count(MediaItem.id)).scalar()
        print(f"\nTotal message groups with media: {total_groups}")
        print(f"Total media items: {total_media}")
    else:
        print("No message groups with media found")

    # Check Media Types Distribution
    print("\n=== Media Types Distribution ===")
    media_types = (
        db.query(MediaItem.media_type, func.count(MediaItem.id))
        .group_by(MediaItem.media_type)
        .all()
    )
    if media_types:
        print_table(media_types, ['Media Type', 'Count'])
    else:
        print("No media items found")

if __name__ == "__main__":
    inspect_db()