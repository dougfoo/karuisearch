"""
Scraper Factory - Centralized management for all property scrapers
"""
import logging
from typing import List, Dict, Optional, Type
from datetime import datetime
import time

from .base_scraper import AbstractPropertyScraper, PropertyData
from .mitsui_scraper import MitsuiNoMoriScraper
from .royal_resort_scraper import RoyalResortScraper  
from .besso_navi_scraper import BessoNaviScraper

logger = logging.getLogger(__name__)

class ScraperFactory:
    """Factory class for managing multiple property scrapers"""
    
    # Registry of available scrapers
    SCRAPERS = {
        'mitsui': {
            'class': MitsuiNoMoriScraper,
            'name': 'Mitsui no Mori',
            'type': 'simple',
            'priority': 3,
            'description': 'WordPress-based luxury property developer'
        },
        'royal_resort': {
            'class': RoyalResortScraper,
            'name': 'Royal Resort Karuizawa',
            'type': 'browser',
            'priority': 1,
            'description': 'JavaScript-heavy luxury resort properties'
        },
        'besso_navi': {
            'class': BessoNaviScraper,
            'name': 'Besso Navi',
            'type': 'browser',
            'priority': 2,
            'description': 'Form-based vacation home search'
        }
    }
    
    def __init__(self, config: dict = None):
        """Initialize scraper factory with configuration"""
        self.config = config or {}
        self.results_cache = {}
        self.scraper_stats = {}
        
        # Default configuration
        self.default_config = {
            'rate_limit': {
                'requests_per_second': 0.33,  # 1 request every 3 seconds
                'random_delay_range': [1, 2]
            },
            'browser_config': {
                'headless': True,
                'wait_timeout': 15,
                'page_load_timeout': 30
            },
            'retry_config': {
                'max_retries': 3,
                'retry_delay': 5
            },
            'validation': {
                'min_properties_per_site': 1,
                'require_karuizawa': True
            }
        }
        
        # Merge with provided config
        if self.config:
            self._merge_config(self.default_config, self.config)
            
    def _merge_config(self, base_config: dict, new_config: dict):
        """Recursively merge configuration dictionaries"""
        for key, value in new_config.items():
            if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
                self._merge_config(base_config[key], value)
            else:
                base_config[key] = value
                
    def get_available_scrapers(self) -> Dict[str, dict]:
        """Get list of available scrapers"""
        return self.SCRAPERS.copy()
        
    def create_scraper(self, scraper_key: str, config: dict = None) -> Optional[AbstractPropertyScraper]:
        """Create a specific scraper instance"""
        if scraper_key not in self.SCRAPERS:
            logger.error(f"Unknown scraper: {scraper_key}")
            return None
            
        scraper_info = self.SCRAPERS[scraper_key]
        scraper_class = scraper_info['class']
        
        # Merge scraper-specific config
        scraper_config = self.default_config.copy()
        if config:
            self._merge_config(scraper_config, config)
            
        try:
            logger.info(f"Creating {scraper_info['name']} scraper")
            return scraper_class(scraper_config)
        except Exception as e:
            logger.error(f"Failed to create {scraper_key} scraper: {e}")
            return None
            
    def scrape_single_site(self, scraper_key: str, config: dict = None) -> List[PropertyData]:
        """Scrape properties from a single site"""
        logger.info(f"Starting scrape for site: {scraper_key}")
        
        start_time = time.time()
        scraper = self.create_scraper(scraper_key, config)
        
        if not scraper:
            logger.error(f"Could not create scraper for {scraper_key}")
            return []
            
        try:
            # Execute scraping
            properties = scraper.scrape_listings()
            
            # Record statistics
            end_time = time.time()
            duration = end_time - start_time
            
            self.scraper_stats[scraper_key] = {
                'properties_found': len(properties),
                'scrape_duration': duration,
                'success': len(properties) > 0,
                'timestamp': datetime.now().isoformat(),
                'scraper_name': self.SCRAPERS[scraper_key]['name']
            }
            
            logger.info(f"Scrape completed for {scraper_key}: {len(properties)} properties in {duration:.1f}s")
            
            # Cache results
            self.results_cache[scraper_key] = {
                'properties': properties,
                'timestamp': time.time(),
                'stats': self.scraper_stats[scraper_key]
            }
            
            return properties
            
        except Exception as e:
            logger.error(f"Error scraping {scraper_key}: {e}")
            
            # Record failed attempt
            self.scraper_stats[scraper_key] = {
                'properties_found': 0,
                'scrape_duration': time.time() - start_time,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'scraper_name': self.SCRAPERS[scraper_key]['name']
            }
            
            return []
        finally:
            # Clean up browser-based scrapers
            if hasattr(scraper, 'close_browser'):
                try:
                    scraper.close_browser()
                except:
                    pass
                    
    def scrape_all_sites(self, site_list: List[str] = None, parallel: bool = False) -> Dict[str, List[PropertyData]]:
        """Scrape properties from multiple sites"""
        if site_list is None:
            # Default to all available scrapers in priority order
            site_list = sorted(self.SCRAPERS.keys(), 
                             key=lambda x: self.SCRAPERS[x]['priority'])
            
        logger.info(f"Starting multi-site scrape: {site_list}")
        
        all_results = {}
        
        if parallel:
            # TODO: Implement parallel scraping (would require threading/async)
            logger.warning("Parallel scraping not yet implemented, falling back to sequential")
            
        # Sequential scraping
        for site_key in site_list:
            if site_key not in self.SCRAPERS:
                logger.warning(f"Skipping unknown scraper: {site_key}")
                continue
                
            logger.info(f"Scraping site {site_key} ({self.SCRAPERS[site_key]['name']})")
            
            try:
                properties = self.scrape_single_site(site_key)
                all_results[site_key] = properties
                
                # Rate limiting between sites
                if len(site_list) > 1:
                    delay = self.default_config['rate_limit']['requests_per_second']
                    logger.info(f"Rate limiting: waiting {delay:.1f}s before next site")
                    time.sleep(1.0 / delay)
                    
            except Exception as e:
                logger.error(f"Failed to scrape {site_key}: {e}")
                all_results[site_key] = []
                
        # Generate summary
        total_properties = sum(len(props) for props in all_results.values())
        successful_sites = sum(1 for props in all_results.values() if len(props) > 0)
        
        logger.info(f"Multi-site scrape completed: {total_properties} properties from {successful_sites}/{len(site_list)} sites")
        
        return all_results
        
    def get_combined_results(self, site_results: Dict[str, List[PropertyData]] = None) -> List[PropertyData]:
        """Combine and deduplicate results from multiple sites"""
        if site_results is None:
            site_results = {k: v['properties'] for k, v in self.results_cache.items()}
            
        all_properties = []
        seen_urls = set()
        
        # Combine all properties
        for site_key, properties in site_results.items():
            for prop in properties:
                # Simple deduplication by source URL
                if prop.source_url and prop.source_url not in seen_urls:
                    seen_urls.add(prop.source_url)
                    all_properties.append(prop)
                elif not prop.source_url:
                    # Include properties without URLs (but they might be duplicates)
                    all_properties.append(prop)
                    
        logger.info(f"Combined results: {len(all_properties)} unique properties")
        return all_properties
        
    def validate_all_results(self, site_results: Dict[str, List[PropertyData]]) -> Dict[str, dict]:
        """Validate results from all sites"""
        validation_report = {}
        
        for site_key, properties in site_results.items():
            if site_key not in self.SCRAPERS:
                continue
                
            scraper = self.create_scraper(site_key)
            if not scraper:
                continue
                
            site_name = self.SCRAPERS[site_key]['name']
            
            # Validate each property
            valid_properties = []
            invalid_properties = []
            
            for prop in properties:
                try:
                    if scraper.validate_property_data(prop):
                        valid_properties.append(prop)
                    else:
                        invalid_properties.append(prop)
                except Exception as e:
                    logger.warning(f"Validation error for {site_key} property: {e}")
                    invalid_properties.append(prop)
                    
            # Generate validation report
            total_count = len(properties)
            valid_count = len(valid_properties)
            success_rate = (valid_count / total_count * 100) if total_count > 0 else 0
            
            validation_report[site_key] = {
                'site_name': site_name,
                'total_properties': total_count,
                'valid_properties': valid_count,
                'invalid_properties': len(invalid_properties),
                'success_rate': success_rate,
                'meets_minimum': valid_count >= self.default_config['validation']['min_properties_per_site'],
                'has_karuizawa_properties': any(prop.contains_karuizawa() for prop in valid_properties)
            }
            
            logger.info(f"Validation for {site_name}: {valid_count}/{total_count} properties valid ({success_rate:.1f}%)")
            
        return validation_report
        
    def get_scraping_stats(self) -> Dict[str, dict]:
        """Get detailed scraping statistics"""
        return self.scraper_stats.copy()
        
    def generate_summary_report(self, site_results: Dict[str, List[PropertyData]] = None) -> dict:
        """Generate comprehensive summary report"""
        if site_results is None:
            site_results = {k: v['properties'] for k, v in self.results_cache.items()}
            
        # Validate all results
        validation_report = self.validate_all_results(site_results)
        
        # Combine results
        combined_properties = self.get_combined_results(site_results)
        
        # Calculate overall statistics  
        total_properties = len(combined_properties)
        total_valid = sum(report['valid_properties'] for report in validation_report.values())
        
        # Price analysis
        prices = []
        for prop in combined_properties:
            if prop.price and '万円' in prop.price:
                try:
                    # Extract numeric part
                    import re
                    numbers = re.findall(r'[\d,]+', prop.price.replace(',', ''))
                    if numbers:
                        price_value = float(numbers[0]) * 10000  # Convert 万円 to yen
                        prices.append(price_value)
                except:
                    continue
                    
        price_stats = {}
        if prices:
            price_stats = {
                'min_price': min(prices),
                'max_price': max(prices),
                'avg_price': sum(prices) / len(prices),
                'count': len(prices)
            }
            
        # Property type distribution
        property_types = {}
        for prop in combined_properties:
            if prop.property_type:
                property_types[prop.property_type] = property_types.get(prop.property_type, 0) + 1
                
        # Generate final report
        report = {
            'summary': {
                'total_sites_scraped': len(site_results),
                'total_properties_found': total_properties,
                'total_valid_properties': total_valid,
                'overall_success_rate': (total_valid / total_properties * 100) if total_properties > 0 else 0,
                'scraping_timestamp': datetime.now().isoformat()
            },
            'site_breakdown': validation_report,
            'price_analysis': price_stats,
            'property_types': property_types,
            'scraping_stats': self.get_scraping_stats()
        }
        
        return report
        
    def export_results(self, site_results: Dict[str, List[PropertyData]], format: str = 'json') -> str:
        """Export results in specified format"""
        if format.lower() == 'json':
            import json
            
            # Convert PropertyData objects to dictionaries
            export_data = {}
            for site_key, properties in site_results.items():
                export_data[site_key] = []
                for prop in properties:
                    prop_dict = {
                        'title': prop.title,
                        'price': prop.price,
                        'location': prop.location,
                        'property_type': prop.property_type,
                        'size_info': prop.size_info,
                        'building_age': prop.building_age,
                        'rooms': prop.rooms,
                        'image_urls': prop.image_urls,
                        'description': prop.description,
                        'source_url': prop.source_url,
                        'scraped_at': prop.scraped_at
                    }
                    export_data[site_key].append(prop_dict)
                    
            return json.dumps(export_data, indent=2, ensure_ascii=False)
            
        elif format.lower() == 'csv':
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.writer(output)
            
            # Write header
            header = ['site', 'title', 'price', 'location', 'property_type', 'size_info', 
                     'building_age', 'rooms', 'image_count', 'source_url', 'scraped_at']
            writer.writerow(header)
            
            # Write data
            for site_key, properties in site_results.items():
                for prop in properties:
                    row = [
                        site_key,
                        prop.title or '',
                        prop.price or '',
                        prop.location or '',
                        prop.property_type or '',
                        prop.size_info or '',
                        prop.building_age or '',
                        prop.rooms or '',
                        len(prop.image_urls) if prop.image_urls else 0,
                        prop.source_url or '',
                        prop.scraped_at or ''
                    ]
                    writer.writerow(row)
                    
            return output.getvalue()
            
        else:
            raise ValueError(f"Unsupported export format: {format}")

def create_factory(config: dict = None) -> ScraperFactory:
    """Convenience function to create a ScraperFactory instance"""
    return ScraperFactory(config)