import orchestrator

if __name__ == "__main__":
    try:
        orchestrator.run_pipeline()
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
