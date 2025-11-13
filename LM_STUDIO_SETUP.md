# LM Studio Setup Guide

## Quick Fix for "400 Bad Request" Errors

The errors you're seeing indicate LM Studio isn't properly configured. Follow these steps:

### 1. Start LM Studio

Open LM Studio application on your Windows machine.

### 2. Load a Model

In the **Search** or **My Models** tab:
- If you don't have `microsoft/phi-4-mini-reasoning`, download it
- Click on the model to load it
- Wait for "Model loaded" confirmation

### 3. Start Local Server

1. Go to **Server** tab in LM Studio
2. Click **Start Server**
3. Verify it shows: `Server running on http://localhost:1234`
4. Keep this server running

### 4. Test the Connection

Open PowerShell and run:

```powershell
curl http://localhost:1234/v1/models
```

You should see JSON output listing your loaded models. Example:
```json
{
  "data": [
    {
      "id": "microsoft/phi-4-mini-reasoning",
      "object": "model",
      ...
    }
  ]
}
```

### 5. Run Your System

Now run:
```powershell
python run_skyrim_agi.py
```

You should see:
```
[PARALLEL] Running LM Studio health check...
[PARALLEL] ✓ LM Studio connection verified
```

## Troubleshooting

### Error: "Cannot connect to LM Studio"

**Cause:** LM Studio not running or server not started

**Fix:**
1. Open LM Studio
2. Go to Server tab
3. Click "Start Server"
4. Wait for "Server running" message

### Error: "LM Studio is running but no models are loaded"

**Cause:** No model selected

**Fix:**
1. Go to Search or My Models tab
2. Click on a model to load it
3. Wait for "Model loaded" confirmation
4. Server will automatically use this model

### Error: Port 1234 already in use

**Cause:** Another application is using port 1234

**Fix Option 1 - Change Port:**
1. In LM Studio Server tab, change port to 1235
2. Update config in your code:
   ```python
   base_url="http://localhost:1235/v1"
   ```

**Fix Option 2 - Kill Process:**
```powershell
# Find what's using port 1234
netstat -ano | findstr :1234

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F
```

### Multiple Model Instances

Your system tries to load 4 different model instances:
- `qwen/qwen3-4b-thinking-2507`
- `microsoft/phi-4-mini-reasoning`
- `microsoft/phi-4-mini-reasoning:2`
- `microsoft/phi-4-mini-reasoning:3`

**Note:** LM Studio typically only loads ONE model at a time. The system will use that one model for all requests.

To avoid confusion:
1. Load just one model (e.g., `microsoft/phi-4-mini-reasoning`)
2. Start the server
3. All requests will go to this model

## Recommended Models

For best performance:

1. **Vision + Reasoning:** `qwen/qwen3-vl-8b` (if you have VRAM)
2. **Fast Reasoning:** `microsoft/phi-4-mini-reasoning` (lighter weight)
3. **Thinking:** `qwen/qwen3-4b-thinking-2507` (extended reasoning)

Choose ONE based on your hardware:
- 8GB+ VRAM: Use Qwen3-VL-8B
- 4-8GB VRAM: Use Phi-4
- <4GB VRAM: Use smaller Phi-4-mini

## Cloud-Only Fallback

If LM Studio continues to fail, you can run cloud-only:

Edit your config to disable local models:
```python
config.use_local_fallback = False
```

System will use only Gemini and Claude (requires API keys).

## Verification Script

Create `test_lmstudio.py`:

```python
import asyncio
from singularis.llm.lmstudio_client import LMStudioClient, LMStudioConfig

async def test():
    config = LMStudioConfig(
        base_url="http://localhost:1234/v1",
        model_name="microsoft/phi-4-mini-reasoning"
    )
    client = LMStudioClient(config)
    
    if await client.health_check():
        print("✓ LM Studio is ready!")
        
        # Try a simple generation
        result = await client.generate(
            prompt="Say hello in one word",
            system_prompt="You are a helpful assistant"
        )
        print(f"Response: {result['content']}")
    else:
        print("✗ LM Studio is not accessible")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(test())
```

Run: `python test_lmstudio.py`

## Success Indicators

When everything works:
- No "400 Bad Request" errors
- Health check passes
- Models respond to prompts
- Clean shutdown with no unclosed sessions

---

**Still having issues?** Check:
1. Windows Firewall isn't blocking localhost:1234
2. Antivirus isn't interfering
3. LM Studio logs (Console tab) for errors
4. Your hardware meets model requirements
