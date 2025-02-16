import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0",  # 修改为 0.0.0.0 允许外部访问
        port=8001, 
        reload=True
    )

