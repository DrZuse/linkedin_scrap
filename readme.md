# LinkedIn Job Scraper
This Python script is designed to scrape job postings from LinkedIn. It uses a list of proxies to send HTTP requests and BeautifulSoup to parse the HTML responses. The script filters job descriptions based on a list of languages and stores the job information in a SQLite database.

## Watch on YouTube
[![Watch the video](https://img.youtube.com/vi/FlmTbkxxNtU/sddefault.jpg)](https://www.youtube.com/watch?v=FlmTbkxxNtU)

## Features
- Uses proxies to send requests
- Parses HTML responses with BeautifulSoup
- Filters job descriptions based on a list of languages
- Stores job information in a SQLite database

## Installation
1. Clone the repository to your local machine.
2. Navigate to the directory containing the script.
3. Run the following command to install the necessary Python libraries:
    ```
    pip install -r requirements.txt
    ```

## How to Use
1. **Import necessary libraries**: The script starts by importing the necessary Python libraries. These include `requests` for sending HTTP requests, `BeautifulSoup` for parsing HTML, `pandas` for data manipulation, `sqlite3` for database operations, and others.
2. **Specify your proxies**: Specify the path to your CSV file with proxies. The CSV format should be: `id;ip;port_http;port_socks5;username;password;internal_ip`.
3. **Define your search query**: Define a search query string by joining multiple keywords. The script will search for jobs that match these keywords.
4. **Specify your database**: Specify the name of the SQLite database and establish a connection. The script will create a table if it doesn't exist for storing job information.
5. **Run the main function**: The main function performs job searches for different experience levels. It sends an HTTP GET request to the job search URL, parses the HTML content using BeautifulSoup, extracts the total number of jobs matching the search criteria, calculates the number of pages to scrape, and retrieves job descriptions for each job ID.
6. **Close the database connection**: After all job searches are completed, the script closes the database connection.

## Requirements
- Python 3.6 or higher
- Libraries: `requests`, `BeautifulSoup`, `pandas`, `sqlite3`, `multiprocessing`, `random`, `langdetect`

## Disclaimer
Please use this script responsibly and in accordance with LinkedIn's terms of service. The author is not responsible for any misuse of this script or any damages that may occur from its use. Always respect the privacy of others and do not use this script for illegal activities. 

## License
This script is released under the MIT License. For more information, please refer to the LICENSE file in the repository. 

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request. 

## Contact
If you have any questions, issues, or suggestions, please open an issue on GitHub. We'll do our best to respond as quickly as possible. 

## Acknowledgements
Thanks to all contributors and users for their support. Your feedback and suggestions are greatly appreciated! 

Happy job hunting! 🎉
