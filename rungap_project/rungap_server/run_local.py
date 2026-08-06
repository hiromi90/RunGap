"""ローカル起動の簡易エントリ：python3 -m rungap_server.run_local"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("rungap_server.app:app", host="127.0.0.1", port=8000, reload=False)
