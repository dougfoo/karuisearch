#!/usr/bin/env python3
"""
Test all 7 working sites together
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.scraper_factory import ScraperFactory
import logging
import json

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_7_sites():
    """Test all 7 working sites"""
    logger.info("Testing all 7 working sites...")
    
    try:
        # Create factory with optimized config for testing
        config = {
            'browser_config': {
                'headless': True,
                'wait_timeout': 15,
                'page_load_timeout': 30
            },
            'rate_limit': {
                'requests_per_second': 0.5,  # Faster for testing
                'random_delay_range': [0.5, 1.0]
            }
        }
        
        factory = ScraperFactory(config)
        
        # Test all sites except SUUMO (which needs more work)
        test_sites = [
            'mitsui', 'royal_resort', 'besso_navi', 
            'resort_innovation', 'tokyu_resort', 'seibu_real_estate', 'resort_home'
        ]
        
        # Run scraping
        logger.info("Starting 7-site system test...")
        site_results = factory.scrape_all_sites(test_sites)
        
        # Generate summary
        report = factory.generate_summary_report(site_results)
        
        logger.info("\n=== 7-SITE SYSTEM TEST RESULTS ===")
        logger.info(f"Total Properties: {report['summary']['total_properties_found']}")
        logger.info(f"Valid Properties: {report['summary']['total_valid_properties']}")
        logger.info(f"Success Rate: {report['summary']['overall_success_rate']:.1f}%")
        
        logger.info("\nSite-by-site breakdown:")
        for site_key, site_report in report['site_breakdown'].items():
            logger.info(f"  {site_report['site_name']}: {site_report['valid_properties']} properties")
        
        # Property type distribution
        if report['property_types']:
            logger.info("\nProperty Types:")
            for prop_type, count in report['property_types'].items():
                logger.info(f"  {prop_type}: {count}")
        
        # Price analysis
        if report['price_analysis']:
            price_stats = report['price_analysis']
            avg_price_millions = price_stats['avg_price'] / 1000000
            logger.info(f"\nPrice Analysis ({price_stats['count']} properties):")
            logger.info(f"  Average: ¥{avg_price_millions:.1f}M")
            logger.info(f"  Range: ¥{price_stats['min_price']/1000000:.1f}M - ¥{price_stats['max_price']/1000000:.1f}M")
        
        if report['summary']['total_properties_found'] > 0:
            logger.info("\n✅ SUCCESS: 7-site system operational!")
            
            # Save results for frontend
            combined_properties = factory.get_combined_results(site_results)
            logger.info(f"Saving {len(combined_properties)} combined properties to mock data...")
            
            # Format for frontend consumption (mock data format)
            mock_properties = []
            for prop in combined_properties[:15]:  # Limit to 15 for demo
                mock_prop = {
                    'id': hash(prop.source_url) % 10000,
                    'title': prop.title or 'Property',
                    'price': prop.price or 'Contact for price',
                    'location': prop.location or 'Karuizawa',
                    'propertyType': prop.property_type or 'House',
                    'size': prop.size_info or '',
                    'rooms': prop.rooms or '',
                    'buildingAge': prop.building_age or '',
                    'description': prop.description or f'Beautiful property in {prop.location}',
                    'imageUrl': prop.image_urls[0] if prop.image_urls else 'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&w=800&q=80',
                    'source': prop.source_url or '',
                    'scrapedAt': prop.scraped_at
                }
                mock_properties.append(mock_prop)
            
            # Write to mock data file
            try:
                with open('src/frontend/src/data/realMockProperties.json', 'w', encoding='utf-8') as f:
                    json.dump(mock_properties, f, indent=2, ensure_ascii=False)
                logger.info("✅ Mock data updated successfully")
            except Exception as e:
                logger.warning(f"Could not save mock data: {e}")
            
        else:
            logger.warning("⚠️ No properties found across all sites")
            
        return site_results
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return {}

if __name__ == "__main__":
    test_7_sites()