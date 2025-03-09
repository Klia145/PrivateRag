import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
from datetime import datetime
import BuildTheRAG
import buildTheKnowledge

class RAGAppWithUpload:
    def __init__(self):
        # 初始化核心组件
        self.rag = BuildTheRAG.RAGSystem()
        self.upload_dir = "DateBase"
        self.processing_flat=False
        self.progress_id=None
        self.processed_dir="ThemessageDatebase"
        self._init_ui()
        self._create_upload_dir()
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        

    def _init_ui(self):
        """构建界面布局"""
        self.window = tk.Tk()
        self.window.title("智能文档问答系统 v2.0")
        self.window.geometry("900x700")

        # 文件上传功能区
        upload_frame = ttk.LabelFrame(self.window, text="文档上传")
        upload_frame.pack(pady=10, padx=20, fill="x")

        self.btn_upload = ttk.Button(
            upload_frame,
            text="选择并上传TXT文档",
            command=self.upload_file
        )
        self.btn_upload.pack(side=tk.LEFT, padx=5)

        self.lbl_upload_status = ttk.Label(upload_frame, text="就绪")
        self.lbl_upload_status.pack(side=tk.RIGHT, padx=10)

        # 问答交互区
        qa_frame = ttk.LabelFrame(self.window, text="智能问答")
        qa_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.txt_question = tk.Text(qa_frame, height=3, wrap=tk.WORD)
        self.txt_question.pack(fill="x", pady=5)

        self.btn_ask = ttk.Button(
            qa_frame,
            text="提交问题",
            command=self.generate_answer
        )
        self.btn_ask.pack(pady=5)

        self.txt_answer = tk.Text(qa_frame, height=15, wrap=tk.WORD)
        self.txt_answer.pack(fill="both", expand=True, pady=5)

        # 状态栏
        self.status_bar = ttk.Label(
            self.window,
            text="系统已就绪",
            relief=tk.SUNKEN
        )
        self.status_bar.pack(side=tk.BOTTOM, fill="x")

    def _create_upload_dir(self):
        """创建上传目录"""
        os.makedirs(self.upload_dir, exist_ok=True)

    def upload_file(self):
        """处理文件上传"""
        
        try:
            filepath = filedialog.askopenfilename(
                title="选择文档",
                filetypes=[("Text Files", "*.txt")]
            )
            
            if not filepath:
                return

            # 生成带时间戳的唯一文件名
            filename = os.path.basename(filepath)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"{timestamp}_{filename}"
            dest_path = os.path.join(self.upload_dir, new_filename)

            # 执行文件拷贝
            shutil.copy(filepath, dest_path)
            
            # 更新界面状态
            self.lbl_upload_status.config(
                text=f"已上传: {new_filename}",
                foreground="green"
            )
            try:
                shutil.copy(filepath, dest_path)
        
        # 更新界面状态
                self.lbl_upload_status.config(
                text=f"已上传: {new_filename}",
                foreground="green"
                )
                self._update_status(f"文档 {new_filename} 上传成功")
        
                if self.process_file(dest_path):  # 直接处理上传的文件
                     self.lbl_upload_status.config(text=f"已处理: {new_filename}", foreground="green")
                else:
                     self.lbl_upload_status.config(text=f"处理失败: {new_filename}", foreground="red")
            except Exception as e:
                self._update_status(f"处理失败: {new_filename}", is_error=True)
        except Exception as e:
            self.lbl_upload_status.config(
                text="上传失败！",
                foreground="red"
            )
            self._update_status(f"错误: {str(e)}", is_error=True)
            messagebox.showerror("上传错误", f"文件上传失败:\n{str(e)}")
        if self.process_file():  # 传入文件路径
            self.lbl_upload_status.config(text=f"已处理: {new_filename}", foreground="green")
    def process_file(self):
        """处理文件"""
        self._start_processing_animation()
        try:
            buildTheKnowledge.process_documents()         
        except Exception as e:
            self._update_status(f"处理失败: {str(e)}", is_error=True)
    def _start_processing_animation(self):
        """显示处理中的动态效果"""
        dots = ['.', '..', '...']
        self.processing_flag = True
        def update_dots(count=[0]):
            if self.processing_flag:
                self.status_bar.config(text=f"处理中{dots[count[0] % 3]}")
                count[0] += 1
                self.progress_id = self.window.after(500, update_dots)
        update_dots()

    def _stop_processing_animation(self, success=True):
        """停止动画"""
        self.processing_flag = False
        if self.progress_id:
            self.window.after_cancel(self.progress_id)
        self.status_bar.config(
            text="处理完成" if success else "处理失败",
            foreground="green" if success else "red"
        )  
    def generate_answer(self):
        """生成问题答案"""
        question = self.txt_question.get("1.0", tk.END).strip()
        if not question:
            messagebox.showwarning("输入错误", "请输入有效问题")
            return

        try:
            self._update_status("正在生成答案...")
            answer = self.rag.generate(question)
            
            self.txt_answer.delete("1.0", tk.END)
            self.txt_answer.insert(tk.END, answer)
            self._update_status("答案生成完成")

        except Exception as e:
            self._update_status(f"生成错误: {str(e)}", is_error=True)
            self.txt_answer.delete("1.0", tk.END)
            self.txt_answer.insert(tk.END, f"系统错误: {str(e)}")

    def _update_status(self, message, is_error=False):
        """更新状态栏"""
        color = "red" if is_error else "black"
        self.status_bar.config(text=message, foreground=color)

    def run(self):
        """启动主循环"""
        self.window.mainloop()

if __name__ == "__main__":
    app = RAGAppWithUpload()
    app.run()