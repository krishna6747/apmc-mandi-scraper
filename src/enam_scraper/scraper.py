class FocusedEnamScraper:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.data = []
        self.setup_driver()

    def setup_driver(self):
        """Setup Chrome driver"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        temp_dir = tempfile.mkdtemp(prefix='chrome_user_data_')
        chrome_options.add_argument(f"--user-data-dir={temp_dir}")

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 15)
            print("✓ Driver setup successful!")
        except Exception as e:
            print(f"Driver setup failed: {e}")
            raise

    def scrape_step_by_step(self, state="Gujarat", max_districts=None):
        """Scrape data step by step with detailed extraction at each level"""
        try:
            print(f"Starting step-by-step scrape for {state}...")
            self.driver.get("https://enam.gov.in/web/apmc-contact-details")
            time.sleep(5)

            # Step 1: Select English language
            self.select_language("English")

            # Step 2: Select state
            state_success = self.select_state(state)
            if not state_success:
                return self.data

            # Step 3: Get and process districts
            districts = self.get_available_districts()
            print(f"Found {len(districts)} districts to process")

            # Process all districts if max_districts is None
            districts_to_process = districts if max_districts is None else districts[:max_districts]

            for i, district in enumerate(districts_to_process):
                print(f"\n--- Processing District {i+1}/{len(districts_to_process)}: {district} ---")

                # Select district and extract data
                self.process_single_district(state, district)

                time.sleep(2)  # Brief pause between districts

            return self.data

        except Exception as e:
            print(f"Error in step-by-step scrape: {e}")
            return self.data
        finally:
            if self.driver:
                self.driver.quit()

    def select_language(self, language="English"):
        """Select language from first dropdown"""
        try:
            dropdowns = self.driver.find_elements(By.CSS_SELECTOR, "select")
            if dropdowns:
                lang_select = Select(dropdowns[0])
                lang_select.select_by_visible_text(language)
                print(f"✓ Selected language: {language}")
                time.sleep(3)
                return True
        except Exception as e:
            print(f"Error selecting language: {e}")
        return False

    def select_state(self, state_name):
        """Select state from dropdown"""
        try:
            dropdowns = self.driver.find_elements(By.CSS_SELECTOR, "select")

            # Find state dropdown (usually second after language)
            state_dropdown = None
            for i, dropdown in enumerate(dropdowns[1:], 1):  # Skip first (language)
                select_obj = Select(dropdown)
                options = [opt.text.strip() for opt in select_obj.options if opt.get_attribute('value')]

                if state_name in options:
                    state_dropdown = dropdown
                    print(f"✓ Found state dropdown at index {i}")
                    break

            if state_dropdown:
                state_select = Select(state_dropdown)
                state_select.select_by_visible_text(state_name)
                print(f"✓ Selected state: {state_name}")
                time.sleep(4)  # Wait for districts to load
                return True
            else:
                print(f"✗ State '{state_name}' not found in dropdowns")
                return False

        except Exception as e:
            print(f"Error selecting state: {e}")
            return False

    def get_available_districts(self):
        """Get list of available districts"""
        try:
            dropdowns = self.driver.find_elements(By.CSS_SELECTOR, "select")

            # Find district dropdown (usually third)
            for dropdown in dropdowns[2:]:  # Skip language and state
                select_obj = Select(dropdown)
                options = select_obj.options

                # Check if this looks like a district dropdown
                option_texts = [opt.text.strip() for opt in options if opt.get_attribute('value')]

                # Filter out placeholder options
                valid_districts = [text for text in option_texts
                                 if not text.lower().startswith('select') and
                                    not text.lower().startswith('all') and
                                    text != '']

                if valid_districts and len(valid_districts) > 5:  # Likely district dropdown
                    print(f"✓ Found {len(valid_districts)} districts")
                    return valid_districts  # CHANGED: Return ALL districts instead of limiting to 10

            print("✗ No district dropdown found")
            return []

        except Exception as e:
            print(f"Error getting districts: {e}")
            return []

    def process_single_district(self, state, district):
        """Process a single district thoroughly"""
        try:
            # Re-select state and district (dropdowns refresh)
            print(f"  Selecting {district}...")

            # Find and select state
            dropdowns = self.driver.find_elements(By.CSS_SELECTOR, "select")
            state_select = Select(dropdowns[1])  # Assuming second dropdown is state
            state_select.select_by_visible_text(state)
            time.sleep(2)

            # Find and select district
            dropdowns = self.driver.find_elements(By.CSS_SELECTOR, "select")
            district_select = Select(dropdowns[2])  # Assuming third dropdown is district
            district_select.select_by_visible_text(district)
            time.sleep(4)  # Wait for data/mandis to load

            print(f"  ✓ Selected {district}, extracting data...")

            # First, try to extract data at district level
            extracted_count = len(self.data)
            self.extract_all_visible_data(state, district)
            new_extractions = len(self.data) - extracted_count

            if new_extractions > 0:
                print(f"  ✓ Extracted {new_extractions} records at district level")
            else:
                print("  ! No data found at district level")

            # Then, check if there are mandis to select
            self.process_mandis_in_district(state, district)

        except Exception as e:
            print(f"  ✗ Error processing district {district}: {e}")

    def process_mandis_in_district(self, state, district):
        """Process individual mandis within a district"""
        try:
            dropdowns = self.driver.find_elements(By.CSS_SELECTOR, "select")

            if len(dropdowns) > 3:  # There might be a mandi dropdown
                mandi_select = Select(dropdowns[3])
                mandi_options = [opt for opt in mandi_select.options
                               if opt.get_attribute('value') and
                               not opt.text.strip().lower().startswith('select')]

                if mandi_options:
                    print(f"    Found {len(mandi_options)} mandis in {district}")

                    # CHANGED: Process ALL mandis instead of limiting to 3
                    for i, mandi_option in enumerate(mandi_options):
                        mandi_text = mandi_option.text.strip()
                        mandi_value = mandi_option.get_attribute('value')

                        print(f"      Processing mandi {i+1}/{len(mandi_options)}: {mandi_text}")

                        try:
                            # Re-select everything
                            dropdowns = self.driver.find_elements(By.CSS_SELECTOR, "select")
                            Select(dropdowns[1]).select_by_visible_text(state)
                            time.sleep(1)
                            Select(dropdowns[2]).select_by_visible_text(district)
                            time.sleep(2)
                            Select(dropdowns[3]).select_by_value(mandi_value)
                            time.sleep(3)

                            # Extract data for this specific mandi
                            extracted_count = len(self.data)
                            self.extract_all_visible_data(state, district, mandi_text)
                            new_extractions = len(self.data) - extracted_count

                            if new_extractions > 0:
                                print(f"        ✓ Extracted {new_extractions} records for {mandi_text}")
                            else:
                                print(f"        ! No specific data found for {mandi_text}")

                        except Exception as e:
                            print(f"        ✗ Error processing mandi {mandi_text}: {e}")
                            continue

        except Exception as e:
            print(f"    Error processing mandis: {e}")

    def extract_all_visible_data(self, state, district, mandi=None):
        """Extract all visible data from current page using multiple methods"""

        # Method 1: Extract from tables
        self.extract_from_tables(state, district, mandi)

        # Method 2: Extract from page text
        self.extract_from_page_text(state, district, mandi)

        # Method 3: Check for specific elements
        self.extract_from_elements(state, district, mandi)

    def extract_from_tables(self, state, district, mandi=None):
        """Extract data from HTML tables"""
        try:
            tables = self.driver.find_elements(By.CSS_SELECTOR, "table")

            for table in tables:
                rows = table.find_elements(By.CSS_SELECTOR, "tr")
                if len(rows) < 2:
                    continue

                # Check if this table contains contact details
                table_text = table.text.lower()
                if any(keyword in table_text for keyword in ['mandi', 'contact', 'address', 'apmc']):

                    record = {
                        'state': state,
                        'district': district,
                        'mandi_name': mandi or '',
                        'address': '',
                        'contact_details': ''
                    }

                    for row in rows:
                        cells = row.find_elements(By.CSS_SELECTOR, "td, th")
                        if len(cells) >= 2:
                            key = cells[0].text.strip().lower()
                            value = cells[1].text.strip()

                            if 'mandi' in key and 'name' in key:
                                record['mandi_name'] = value
                            elif 'address' in key:
                                record['address'] = value
                            elif 'contact' in key:
                                record['contact_details'] = value
                            elif 'state' in key and not record['state']:
                                record['state'] = value

                    # Only add if we found meaningful data AND address is not empty
                    if (record['mandi_name'] or record['contact_details']) and record['address'].strip():
                        self.data.append(record)
                        print(f"      ✓ Table extraction: {record['mandi_name'] or 'Unknown'}")

        except Exception as e:
            print(f"      Error in table extraction: {e}")

    def extract_from_page_text(self, state, district, mandi=None):
        """Extract data from plain page text"""
        try:
            body = self.driver.find_element(By.TAG_NAME, "body")
            page_text = body.text

            # Look for contact details patterns
            if any(keyword in page_text.lower() for keyword in ['contact details', 'mandi name', 'apmc']):

                # Try to find structured information
                lines = page_text.split('\n')
                record = None

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    # Look for key indicators
                    if 'mandi name' in line.lower() and ':' in line:
                        if not record:
                            record = {
                                'state': state,
                                'district': district,
                                'mandi_name': mandi or '',
                                'address': '',
                                'contact_details': ''
                            }

                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            record['mandi_name'] = parts[1].strip()

                    elif record and 'address' in line.lower() and ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            record['address'] = parts[1].strip()

                    elif record and 'contact' in line.lower() and ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            record['contact_details'] = parts[1].strip()

                if record and record['address'].strip() and (record['mandi_name'] or record['contact_details']):
                    self.data.append(record)
                    print(f"      ✓ Text extraction: {record['mandi_name'] or 'Unknown'}")

        except Exception as e:
            print(f"      Error in text extraction: {e}")

    def extract_from_elements(self, state, district, mandi=None):
        """Extract data from specific page elements"""
        try:
            # Look for common result containers
            selectors = [
                '.result', '.contact-details', '.mandi-details',
                '.table-responsive', '.search-result', '.data-row',
                '[class*="result"]', '[class*="contact"]', '[class*="mandi"]'
            ]

            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

                for element in elements:
                    element_text = element.text.strip()
                    if len(element_text) > 20 and any(keyword in element_text.lower()
                                                     for keyword in ['mandi', 'contact', 'apmc']):

                        # Only extract if we can find address information
                        if any(addr_keyword in element_text.lower() for addr_keyword in ['address', 'road', 'pin', 'market']):
                            record = {
                                'state': state,
                                'district': district,
                                'mandi_name': mandi or self.extract_mandi_name_from_text(element_text),
                                'address': self.extract_address_from_text(element_text),
                                'contact_details': self.extract_contact_from_text(element_text)
                            }

                            # Only add if address is found
                            if record['address'].strip():
                                self.data.append(record)
                                print(f"      ✓ Element extraction: {record['mandi_name'] or 'Unknown'}")
                                break  # Only take first valid match per selector

        except Exception as e:
            print(f"      Error in element extraction: {e}")

    def extract_mandi_name_from_text(self, text):
        """Extract mandi name from text"""
        lines = text.split('\n')
        for line in lines:
            if 'mandi name' in line.lower() and ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    return parts[1].strip()
            elif 'apmc' in line.lower() and len(line) < 100:
                return line.strip()
        return ''

    def extract_address_from_text(self, text):
        """Extract address from text"""
        lines = text.split('\n')
        for line in lines:
            if 'address' in line.lower() and ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    return parts[1].strip()
            elif any(keyword in line.lower() for keyword in ['road', 'pin', 'market', 'commiti']) and len(line) > 20:
                return line.strip()
        return ''

    def extract_contact_from_text(self, text):
        """Extract contact details from text"""
        lines = text.split('\n')
        contact_info = []

        for line in lines:
            line = line.strip()
            if 'contact' in line.lower() and ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    contact_info.append(parts[1].strip())
            elif '@' in line or any(char.isdigit() for char in line):
                # Look for email or phone patterns
                if len(line) < 50 and (line.count('@') == 1 or any(char.isdigit() for char in line)):
                    contact_info.append(line)

        return ', '.join(contact_info)

    def save_results(self):
        """Save results to CSV with data cleaning"""
        if self.data:
            # Create DataFrame
            df = pd.DataFrame(self.data)

            # Clean and filter data
            df = self.clean_data(df)

            if len(df) > 0:
                filename = f"enam_clean_data_{int(time.time())}.csv"
                df.to_csv(filename, index=False)
                print(f"\n🎉 SUCCESS: Saved {len(df)} clean records to {filename}")

                # Show summary
                print(f"\nData Summary:")
                print(f"- Total records: {len(df)}")
                print(f"- States: {df['state'].nunique()}")
                print(f"- Districts: {df['district'].nunique()}")
                print(f"- Records with addresses: {df['address'].notna().sum()}")
                print(f"- Records with contact details: {df['contact_details'].notna().sum()}")

                print(f"\nSample records:")
                for i, row in df.head().iterrows():
                    print(f"{i+1}. {row['mandi_name']} | {row['district']} | Address: {row['address'][:50]}...")

                return df
            else:
                print("\n❌ No valid data after cleaning")
                return None
        else:
            print("\n❌ No data extracted")
            return None

    def clean_data(self, df):
        """Clean and filter the extracted data"""
        print(f"Cleaning data: {len(df)} raw records")

        # Remove records without address
        df = df[df['address'].notna() & (df['address'].str.strip() != '')]
        print(f"After address filter: {len(df)} records")

        # Remove duplicate records (same mandi_name + address)
        df = df.drop_duplicates(subset=['mandi_name', 'address'], keep='first')
        print(f"After removing duplicates: {len(df)} records")

        # Clean text fields
        for col in ['mandi_name', 'address', 'contact_details']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
                df[col] = df[col].replace('nan', '')

        # Remove records where mandi_name is empty or just generic text
        invalid_mandi_names = ['', 'unknown', 'element_', 'debug_', 'nan', 'none']
        df = df[~df['mandi_name'].str.lower().isin(invalid_mandi_names)]
        df = df[~df['mandi_name'].str.lower().str.startswith('element_')]
        df = df[~df['mandi_name'].str.lower().str.startswith('debug_')]
        print(f"After mandi name filter: {len(df)} records")

        # Ensure minimum data quality - must have either mandi_name or meaningful address
        df = df[
            (df['mandi_name'].str.len() > 3) |
            (df['address'].str.len() > 20)
        ]
        print(f"After quality filter: {len(df)} records")

        # Reset index
        df = df.reset_index(drop=True)

        return df

# Modified usage function to scrape ALL districts and mandis
def run_focused_scraper(state="Maharashtra", max_districts=None):
    """Run the focused scraper for ALL districts and mandis"""
    scraper = FocusedEnamScraper()
    try:
        data = scraper.scrape_step_by_step(state, max_districts)
        return scraper.save_results()
    except Exception as e:
        print(f"Scraper failed: {e}")
        return None

# Run it for ALL districts and mandis in Gujarat
if __name__ == "__main__":
    print("🚀 Starting complete Gujarat eNAM data extraction...")
    print("⚠️  This will take considerable time as it processes ALL districts and mandis")
    df = run_focused_scraper("Gujarat", max_districts=None)  # None means ALL districts