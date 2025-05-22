import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.syntax import Syntax
import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

load_dotenv()
console = Console()

@click.group()
@click.version_option(version="0.1.0")
def main():
    """🚀 CodeAssist: LLM-Based Code Completion and Review Tool
    
    AI-powered code completion, review, and explanation.
    """
    pass

@main.command()
def hello():
    """Test if CodeAssist is working"""
    console.print("✅ [green]CodeAssist is working perfectly![/green]")
    console.print("🤖 Ready to help with your code!")
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "your_openai_api_key_here":
        console.print("🔑 [green]OpenAI API Key: Configured[/green]")
        console.print("🚀 [bold blue]AI features are ready![/bold blue]")
    else:
        console.print("⚠️  [yellow]OpenAI API Key: Not configured[/yellow]")
        console.print("💡 Add your key to .env file: OPENAI_API_KEY=your_key")

@main.command()
@click.argument('code', required=False)
@click.option('--file', '-f', type=click.Path(exists=True), help='Complete code from file')
def complete(code, file):
    """✨ Complete your code with AI assistance"""
    if not code and not file:
        console.print("❌ Please provide code to complete")
        console.print("💡 Examples:")
        console.print("  codeassist complete 'def fibonacci(n):'")
        console.print("  codeassist complete --file script.py")
        return
    
    # Check API key first
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        console.print("❌ [red]OpenAI API key not configured[/red]")
        console.print("💡 Set your API key in .env file: OPENAI_API_KEY=your_key")
        console.print("🔗 Get your key at: https://platform.openai.com/api-keys")
        return
    
    if file:
        code = Path(file).read_text()
        console.print(f"📁 Completing code from: {file}")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🤖 AI is completing your code...", total=None)
        
        try:
            # Import here to avoid import errors if OpenAI isn't installed
            from models.llm_client import LLMClient
            
            # Simple completion for now
            llm = LLMClient()
            
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert Python programmer. Complete the code naturally and efficiently. Only return the completion, not the original code."
                },
                {
                    "role": "user",
                    "content": f"Complete this Python code:\n\n```python\n{code}\n```\n\nProvide only the completion code, properly formatted and indented."
                }
            ]
            
            completion = asyncio.run(llm.generate(messages, temperature=0.3, max_tokens=500))
            progress.stop()
            
            # Display original code
            console.print("\n📝 [bold blue]Original Code:[/bold blue]")
            syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, border_style="blue"))
            
            # Display completion
            console.print("\n✨ [bold green]AI Completion:[/bold green]")
            completion_syntax = Syntax(completion, "python", theme="monokai", line_numbers=True)
            console.print(Panel(completion_syntax, border_style="green"))
            
        except Exception as e:
            progress.stop()
            console.print(f"❌ [red]Error: {str(e)}[/red]")
            console.print("💡 Make sure your OpenAI API key is valid and you have credits")

@main.command()
@click.argument('code', required=False)
@click.option('--file', '-f', type=click.Path(exists=True), help='Review code from file')
def review(code, file):
    """🔍 Review your code and get improvement suggestions"""
    if not code and not file:
        console.print("❌ Please provide code to review")
        console.print("💡 Examples:")
        console.print("  codeassist review 'for i in range(len(data)): print(data[i])'")
        console.print("  codeassist review --file script.py")
        return
    
    # Check API key first
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        console.print("❌ [red]OpenAI API key not configured[/red]")
        console.print("💡 Set your API key in .env file: OPENAI_API_KEY=your_key")
        return
    
    if file:
        code = Path(file).read_text()
        console.print(f"📁 Reviewing code from: {file}")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🔍 AI is analyzing your code...", total=None)
        
        try:
            from models.llm_client import LLMClient
            
            llm = LLMClient()
            
            messages = [
                {
                    "role": "system",
                    "content": """You are an expert code reviewer. Analyze the code for:
                    1. Code quality and best practices
                    2. Performance issues
                    3. Security vulnerabilities  
                    4. Readability and maintainability
                    5. Potential bugs or edge cases
                    
                    Provide constructive feedback with specific suggestions for improvement."""
                },
                {
                    "role": "user",
                    "content": f"Please review this Python code:\n\n```python\n{code}\n```"
                }
            ]
            
            review = asyncio.run(llm.generate(messages, temperature=0.3, max_tokens=800))
            progress.stop()
            
            # Display code being reviewed
            console.print("\n📝 [bold blue]Code Under Review:[/bold blue]")
            syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, border_style="blue"))
            
            # Display review
            console.print("\n🔍 [bold yellow]AI Code Review:[/bold yellow]")
            console.print(Panel(review, border_style="yellow", title="Review Results"))
            
        except Exception as e:
            progress.stop()
            console.print(f"❌ [red]Error: {str(e)}[/red]")
            console.print("💡 Make sure your OpenAI API key is valid")

@main.command()
@click.argument('code', required=False)
@click.option('--file', '-f', type=click.Path(exists=True), help='Explain code from file')
def explain(code, file):
    """📚 Get natural language explanation of your code"""
    if not code and not file:
        console.print("❌ Please provide code to explain")
        console.print("💡 Examples:")
        console.print("  codeassist explain 'lambda x: x**2 + 2*x + 1'")
        console.print("  codeassist explain --file algorithm.py")
        return
    
    # Check API key first
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        console.print("❌ [red]OpenAI API key not configured[/red]")
        console.print("💡 Set your API key in .env file: OPENAI_API_KEY=your_key")
        return
    
    if file:
        code = Path(file).read_text()
        console.print(f"📁 Explaining code from: {file}")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("📚 AI is explaining your code...", total=None)
        
        try:
            from models.llm_client import LLMClient
            
            llm = LLMClient()
            
            messages = [
                {
                    "role": "system",
                    "content": """You are a helpful programming tutor. Explain code in clear, simple language. 
                    Break down complex concepts and explain the purpose and functionality step by step."""
                },
                {
                    "role": "user",
                    "content": f"Please explain what this Python code does:\n\n```python\n{code}\n```"
                }
            ]
            
            explanation = asyncio.run(llm.generate(messages, temperature=0.5, max_tokens=600))
            progress.stop()
            
            # Display code being explained
            console.print("\n📝 [bold blue]Code to Explain:[/bold blue]")
            syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, border_style="blue"))
            
            # Display explanation
            console.print("\n📚 [bold cyan]AI Explanation:[/bold cyan]")
            console.print(Panel(explanation, border_style="cyan", title="Code Explanation"))
            
        except Exception as e:
            progress.stop()
            console.print(f"❌ [red]Error: {str(e)}[/red]")
            console.print("💡 Make sure your OpenAI API key is valid")

@main.command()
def status():
    """📊 Check CodeAssist status and configuration"""
    console.print("\n🚀 [bold blue]CodeAssist Status[/bold blue]")
    console.print("📦 Version: 0.1.0")
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "your_openai_api_key_here":
        console.print("✅ [green]OpenAI API Key: Configured[/green]")
        console.print("🚀 [bold blue]All AI features are ready![/bold blue]")
    else:
        console.print("❌ [red]OpenAI API Key: Not found[/red]")
        console.print("💡 Set your API key in .env file")
        console.print("🔗 Get your key at: https://platform.openai.com/api-keys")
    
    console.print("\n🎯 Available Commands:")
    console.print("  • [cyan]codeassist hello[/cyan] - Test installation")
    console.print("  • [cyan]codeassist complete[/cyan] - Complete your code with AI")
    console.print("  • [cyan]codeassist review[/cyan] - Get AI code review") 
    console.print("  • [cyan]codeassist explain[/cyan] - Get AI code explanation")
    console.print("  • [cyan]codeassist status[/cyan] - Show this status")

if __name__ == '__main__':
    main()