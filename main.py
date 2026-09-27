if __name__ == "__main__":
    if not RAILWAY_DOMAIN:
        logger.info("Running in polling mode (local dev)")
        app.run_polling()
    else:
        logger.info(f"Starting webhook server on port {PORT}")
        flask_app.run(host="0.0.0.0", port=PORT)
