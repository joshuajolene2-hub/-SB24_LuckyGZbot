if __name__ == "__main__":
    # Force webhook mode for Railway (always)
    if RAILWAY_DOMAIN:
        logger.info(f"Starting webhook server on port {PORT}")
        flask_app.run(host="0.0.0.0", port=PORT)
    else:
        # This is only for local testing
        logger.info("Running in polling mode (local dev)")
        app.run_polling()
