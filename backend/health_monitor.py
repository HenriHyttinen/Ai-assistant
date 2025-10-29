#!/usr/bin/env python3
"""
Backend Health Monitor
Monitors the backend health and automatically restarts if needed
"""
import time
import requests
import subprocess
import signal
import os
import sys
from datetime import datetime

class BackendHealthMonitor:
    def __init__(self, backend_url="http://localhost:8000", check_interval=30):
        self.backend_url = backend_url
        self.check_interval = check_interval
        self.restart_count = 0
        self.max_restarts = 5
        self.backend_process = None
        
    def is_backend_healthy(self):
        """Check if backend is responding"""
        try:
            response = requests.get(f"{self.backend_url}/", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def start_backend(self):
        """Start the backend server"""
        try:
            print(f"[{datetime.now()}] Starting backend server...")
            
            # Change to backend directory
            backend_dir = os.path.join(os.path.dirname(__file__))
            os.chdir(backend_dir)
            
            # Start uvicorn with gaming-optimized settings
            cmd = [
                "python", "-m", "uvicorn", "main:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--workers", "1",
                "--timeout-keep-alive", "600",
                "--limit-concurrency", "500",
                "--backlog", "1000",
                "--access-log"
            ]
            
            self.backend_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid
            )
            
            # Wait a bit for startup
            time.sleep(5)
            
            if self.is_backend_healthy():
                print(f"[{datetime.now()}] Backend started successfully")
                return True
            else:
                print(f"[{datetime.now()}] Backend failed to start properly")
                return False
                
        except Exception as e:
            print(f"[{datetime.now()}] Error starting backend: {e}")
            return False
    
    def stop_backend(self):
        """Stop the backend server"""
        if self.backend_process:
            try:
                print(f"[{datetime.now()}] Stopping backend server...")
                os.killpg(os.getpgid(self.backend_process.pid), signal.SIGTERM)
                self.backend_process.wait(timeout=10)
                print(f"[{datetime.now()}] Backend stopped")
            except:
                try:
                    os.killpg(os.getpgid(self.backend_process.pid), signal.SIGKILL)
                except:
                    pass
            finally:
                self.backend_process = None
    
    def restart_backend(self):
        """Restart the backend server"""
        if self.restart_count >= self.max_restarts:
            print(f"[{datetime.now()}] Maximum restart attempts reached ({self.max_restarts})")
            return False
            
        self.restart_count += 1
        print(f"[{datetime.now()}] Restarting backend (attempt {self.restart_count}/{self.max_restarts})")
        
        self.stop_backend()
        time.sleep(2)
        
        if self.start_backend():
            self.restart_count = 0  # Reset counter on successful restart
            return True
        else:
            return False
    
    def run(self):
        """Main monitoring loop"""
        print(f"[{datetime.now()}] Starting backend health monitor...")
        
        # Start backend initially
        if not self.start_backend():
            print(f"[{datetime.now()}] Failed to start backend initially")
            return
        
        try:
            while True:
                time.sleep(self.check_interval)
                
                if not self.is_backend_healthy():
                    print(f"[{datetime.now()}] Backend is not healthy, attempting restart...")
                    if not self.restart_backend():
                        print(f"[{datetime.now()}] Failed to restart backend, exiting monitor")
                        break
                else:
                    # Reset restart count on successful health check
                    if self.restart_count > 0:
                        self.restart_count = 0
                        print(f"[{datetime.now()}] Backend is healthy, reset restart counter")
                        
        except KeyboardInterrupt:
            print(f"[{datetime.now()}] Monitor stopped by user")
        except Exception as e:
            print(f"[{datetime.now()}] Monitor error: {e}")
        finally:
            self.stop_backend()

if __name__ == "__main__":
    monitor = BackendHealthMonitor()
    monitor.run()

