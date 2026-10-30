import os

import uvicorn

if __name__ == "__main__":
    # Windows/Hyper-V often reserves 8080 (netsh excludedportrange); override with PORT=8300
    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run("app.main:app", host="127.0.0.1", port=port, reload=True)
