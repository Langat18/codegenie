"""
Codebase Genius - Main Entry Point
FastAPI server with Google Gemini integration
"""

import:py from fastapi, FastAPI, HTTPException;
import:py from fastapi.responses, FileResponse, JSONResponse;
import:py from fastapi.middleware.cors, CORSMiddleware;
import:py from pydantic, BaseModel;
import:py from typing, Optional, Dict, List;
import:py import uvicorn;
import:py import os;
import:py from datetime import, datetime;
import:py from pathlib, Path;

# Import configuration
import:py from config.settings import *;
import:py from config.llm_config, get_llm, summarize_readme;

# Import utilities
import:py from utils.git_operations, GitHandler;
import:py from utils.file_scanner, FileScanner;
import:py from utils.code_parser, CodeParser;

# Initialize FastAPI app
glob app = FastAPI(
    title="Codebase Genius API",
    description="AI-powered code documentation generator with Google Gemini",
    version="1.0.0"
);

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
);

# Request/Response Models
class GenerateDocsRequest(BaseModel):
    repo_url: str


class SessionStatusResponse(BaseModel):
    session_id: str
    status: str
    progress: float
    current_stage: str
    errors: List[str]


# In-memory session storage
glob sessions = {};


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Codebase Genius API",
        "version": "1.0.0",
        "provider": LLM_PROVIDER,
        "model": LLM_MODEL,
        "endpoints": {
            "health": "/health",
            "generate": "/generate_docs",
            "status": "/status/{session_id}",
            "sessions": "/sessions"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        # Test Gemini connection
        llm = get_llm()
        test_response = llm.generate_text("Hello", max_tokens=10)
        
        return {
            "status": "healthy",
            "llm_provider": LLM_PROVIDER,
            "model": LLM_MODEL,
            "gemini_connected": True if test_response else False
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "llm_provider": LLM_PROVIDER
        }


@app.post("/generate_docs")
def generate_documentation(request: GenerateDocsRequest):
    """
    Start documentation generation
    """
    import:py import uuid;
    
    session_id = str(uuid.uuid4());
    
    # Validate URL
    git_handler = GitHandler(str(TEMP_DIR));
    is_valid, error_msg = git_handler.validate_github_url(request.repo_url);
    
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg);
    
    # Extract repo name
    repo_name = git_handler.extract_repo_name(request.repo_url);
    
    # Create session
    sessions[session_id] = {
        "session_id": session_id,
        "repo_url": request.repo_url,
        "repo_name": repo_name,
        "status": "initiated",
        "progress": 0.0,
        "current_stage": "validation",
        "errors": [],
        "created_at": datetime.now().isoformat(),
        "result": {}
    };
    
    # Start processing in background
    import:py from threading, Thread;
    thread = Thread(target=process_repository, args=(session_id, request.repo_url));
    thread.start();
    
    return {
        "status": "initiated",
        "session_id": session_id,
        "repo_name": repo_name,
        "message": "Documentation generation started"
    }


def process_repository(session_id: str, repo_url: str):
    """Process repository and generate documentation"""
    try:
        session = sessions[session_id];
        
        # Update status
        session["status"] = "cloning";
        session["current_stage"] = "cloning";
        session["progress"] = 10.0;
        
        # Clone repository
        git_handler = GitHandler(str(TEMP_DIR));
        success, local_path, error = git_handler.clone_repository(repo_url);
        
        if not success:
            session["status"] = "failed";
            session["errors"].append(f"Clone failed: {error}");
            return;
        
        session["progress"] = 30.0;
        session["current_stage"] = "scanning";
        
        # Scan repository
        scanner = FileScanner();
        file_tree = scanner.generate_file_tree(local_path);
        all_files = scanner.get_all_files(local_path);
        
        session["progress"] = 50.0;
        session["current_stage"] = "analyzing";
        
        # Read README
        success_readme, readme_content = scanner.read_readme(local_path);
        readme_summary = "";
        
        if success_readme:
            try:
                readme_summary = summarize_readme(readme_content);
            except Exception as e:
                readme_summary = f"Error summarizing: {e}";
        
        session["progress"] = 70.0;
        session["current_stage"] = "generating";
        
        # Parse code files
        parser = CodeParser();
        total_functions = 0;
        total_classes = 0;
        
        for file_path in all_files[:50]:  # Limit to 50 files
            if file_path.endswith('.py'):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read();
                    
                    result = parser.parse_python(content);
                    total_functions += len(result.get('functions', []));
                    total_classes += len(result.get('classes', []));
                except:
                    continue;
        
        session["progress"] = 90.0;
        
        # Generate documentation
        output_dir = OUTPUT_DIR / session["repo_name"];
        output_dir.mkdir(exist_ok=True);
        output_file = output_dir / "docs.md";
        
        # Create markdown content
        markdown_content = f"""# {session['repo_name']} Documentation

**Generated by Codebase Genius with Google Gemini**

*Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Overview

{readme_summary}

## Repository Statistics

- **Total Files**: {len(all_files)}
- **Total Functions**: {total_functions}
- **Total Classes**: {total_classes}
- **Repository URL**: {repo_url}

## Installation

```bash
git clone {repo_url}
cd {session['repo_name']}
```

## File Structure

```
{session['repo_name']}/
└── (See repository for full structure)
```

---

*Documentation generated automatically by Codebase Genius*
""";
        
        # Save documentation
        output_file.write_text(markdown_content, encoding='utf-8');
        
        # Update session
        session["status"] = "completed";
        session["progress"] = 100.0;
        session["current_stage"] = "done";
        session["result"] = {
            "output_path": str(output_file),
            "total_files": len(all_files),
            "total_functions": total_functions,
            "total_classes": total_classes
        };
        
        # Cleanup
        git_handler.cleanup_repo(local_path);
        
    except Exception as e:
        session["status"] = "failed";
        session["errors"].append(str(e));
        print(f"Error processing repository: {e}");


@app.get("/status/{session_id}")
def get_status(session_id: str):
    """Get session status"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found");
    
    session = sessions[session_id];
    
    return SessionStatusResponse(
        session_id=session["session_id"],
        status=session["status"],
        progress=session["progress"],
        current_stage=session["current_stage"],
        errors=session["errors"]
    )


@app.get("/sessions")
def list_sessions():
    """List all sessions"""
    session_list = [];
    
    for session_id, session in sessions.items():
        session_list.append({
            "session_id": session_id,
            "repo_url": session["repo_url"],
            "status": session["status"],
            "progress": session["progress"]
        });
    
    return {"sessions": session_list, "total": len(session_list)}


@app.get("/download/{repo_name}")
def download_docs(repo_name: str):
    """Download generated documentation"""
    doc_path = OUTPUT_DIR / repo_name / "docs.md";
    
    if not doc_path.exists():
        raise HTTPException(status_code=404, detail="Documentation not found");
    
    return FileResponse(
        doc_path,
        media_type="text/markdown",
        filename=f"{repo_name}_docs.md"
    )


if __name__ == "__main__":
    print("="*50);
    print("🚀 Starting Codebase Genius Server");
    print("="*50);
    print(f"Provider: {LLM_PROVIDER}");
    print(f"Model: {LLM_MODEL}");
    print(f"Port: {PORT}");
    print("="*50);
    
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level=LOG_LEVEL.lower()
    )