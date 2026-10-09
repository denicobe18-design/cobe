from typing import List, Dict, Union
from dataclasses import dataclass


@dataclass(frozen=True)
class Opportunity:
    """Dataclass representing a structured arbitrage opportunity."""
    id: str
    name: str
    source_url: str
    source_price: float
    target_price: float
    gross_profit: float
    roi_percent: float


def calculate_profit(source_price: float, target_price: float) -> tuple[float, float]:
    """
    Calculates gross profit and ROI percentage.

    Args:
        source_price: The base cost of the product.
        target_price: The selling price on the target platform.

    Returns:
        A tuple containing (gross_profit, roi_percent).
    """
    if source_price <= 0:
        return 0.0, 0.0
    
    gross_profit = target_price - source_price
    roi_percent = (gross_profit / source_price) * 100
    
    return round(gross_profit, 2), round(roi_percent, 2)


def structure_opportunities(
    source_data: List[Dict[str, Union[str, float]]],
    target_data: List[Dict[str, Union[str, float]]]
) -> List[Opportunity]:
    """
    Matches product data from source against target and structures opportunities.

    Currently uses a simple index-based matching for demonstration. In production,
    this would use semantic product name matching or ID matching.

    Args:
        source_data: Scraped data from source site.
        target_data: Scraped data from target site.

    Returns:
        A list of structured Opportunity objects.
    """
    opportunities = []
    
    # Simple direct matching by index for initial version
    max_items = min(len(source_data), len(target_data))
    
    for i in range(max_items):
        src_item = source_data[i]
        tgt_item = target_data[i]
        
        src_price = float(src_item.get("price", 0.0))
        tgt_price = float(tgt_item.get("price", 0.0))
        
        gross, roi = calculate_profit(src_price, tgt_price)
        
        # Arbitrage filter: only include profitable items
        if gross > 0:
            opp = Opportunity(
                id=str(src_item.get("id", i)),
                name=str(src_item.get("name", "Unknown Product")),
                source_url=str(src_item.get("url", "#")),
                source_price=src_price,
                target_price=tgt_price,
                gross_profit=gross,
                roi_percent=roi
            )
            opportunities.append(opp)
            
    # Sort by ROI descending for immediate maximum impact
    opportunities.sort(key=lambda x: x.roi_percent, reverse=True)
            
    return opportunities


if __name__ == "__main__":
    # Internal test example
    dummy_source = [
        {"id": "a1", "name": "Brutal Widget", "price": 10.0, "url": "http://src.com/1"},
        {"id": "a2", "name": "Impact Mouse", "price": 50.0, "url": "http://src.com/2"},
    ]
    dummy_target = [
        {"price": 19.99}, # Proft: 9.99, ROI: ~99.9
        {"price": 45.0},  # Profit: -5.0 (filtered)
    ]
    
    results = structure_opportunities(dummy_source, dummy_target)
    
    print(f"Found {len(results)} profitable opportunities.")
    for res in results:
        print(f"Product: {res.name} | Profit: ${res.gross_profit} | ROI: {res.roi_percent}%")