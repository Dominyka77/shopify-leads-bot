from flask import Flask, request, jsonify
from shopify_scraper import run_scraper

app = Flask(__name__)

@app.route("/scrape", methods=["POST"])
def scrape():
    try:
        keywords = request.form.get("niche_keywords", "")
        scrape_emails = request.form.get("scrape_emails") == "on"

        if not keywords:
            return jsonify({"error": "No keywords provided."}), 400

        keyword_list = [kw.strip() for kw in keywords.split(",")]
        print("🔍 Keywords received:", keyword_list)
        print("📧 Email scraping enabled:", scrape_emails)

        # 🧠 Safe mode logic passed to scraper
        run_scraper(keyword_list, scrape_emails=scrape_emails)

        return jsonify({
            "csv": "shopify_leads.csv",
            "message": "Scraping complete."
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting Flask server on port {port}...")
    app.run(host="0.0.0.0", port=port)




