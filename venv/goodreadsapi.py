import os, requests

"""
Call the GoodReads API with the given ISBN
"""
def get_good_reads_data(isbn):
    """
    Get book data from GoodReads API

        Parameters:
            isbn (string): The desired book isbn.

        Returns:
            JSON: GoodReads JSON Object.
    """
    api_key = os.getenv("GOODREADS_APIKEY")
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": api_key, "isbns": isbn})
    data = res.json()
    return data["books"][0]