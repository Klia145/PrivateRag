import tkinter as tk
from tkinter import ttk, scrolledtext
import BuildTheRAG

class RAGApp:
    def __init__(self):
        self.rag = BuildTheRAG.RAGSystem()
        self.window = tk.Tk()
        self.window.title("RAG 问答系统")
        self.window.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        self.question_label = ttk.Label(self.window, text="请输入问题：")
        self.question_label.pack(pady=10)
        
        self.question_entry = ttk.Entry(self.window, width=100)
        self.question_entry.pack(pady=5)
        self.submit_btn = ttk.Button(
            self.window, 
            text="获取答案", 
            command=self.generate_answer
        )
        self.submit_btn.pack(pady=10)
        self.answer_area = scrolledtext.ScrolledText(
            self.window, 
            wrap=tk.WORD, 
            width=100, 
            height=20
        )
        self.answer_area.pack(pady=10)
        self.status_bar = ttk.Label(
            self.window, 
            text="就绪", 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X)

    def generate_answer(self):
        self.answer_area.delete(1.0, tk.END)
        self.status_bar.config(text="正在生成答案...")
        try:
            question = self.question_entry.get()
            answer = self.rag.generate(question)
            self.answer_area.insert(tk.END, f"问题：{question}\n\n答案：{answer}")
            self.status_bar.config(text="完成")
        except Exception as e:
            self.answer_area.insert(tk.END, f"错误：{str(e)}")
            self.status_bar.config(text="生成失败")

if __name__ == "__main__":
    app = RAGApp()
    app.window.mainloop()