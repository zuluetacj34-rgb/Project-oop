import tkinter as tk
from tkinter import ttk, messagebox, simpledialog,filedialog
from database import Database
from classes import Student,ClassSession,AttendanceManager
import datetime
import csv
class LoginWindow:
    def __init__(self,root,db:Database,on_success):
        self.root = root
        self.db = db
        self.on_success = on_success
        self.frame = ttk.Frame(root,padding=20)
        self.frame.pack(expand=True)

        ttk.Label(self.frame,text="Username").grid(row=0,column=0,sticky=tk.E)
        self.user_entry =ttk.Entry(self.frame)
        self.user_entry.grid(row=1,column=1)

        ttk.Label(self.frame,text="Password").grid(row=1,column=0,sticky=tk.E)
        self.pass_entry = ttk.Entry(self.frame,show="*")
        self.pass_entry.grid(row=1,column=1)

        login_btn = ttk.Button(self.frame,text="Login",command=self.try_login)
        login_btn.grid(row=2,column=0,columnspan=2,pady=10)
    
    def try_login(self):
        username =self.user_entry.get().strip()
        password=self.pass_entry.get().strip()
        role= self.db.verify_user(username,password)
        if role:
            messagebox.showinfo("Login", f"Welcome{username}({role})")
            self.frame.destroy()
            self.on_success(username,password)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

class MainApp:
    def __init__(self,root,db:Database,username:str,role:str):
        self.root=root
        self.db=db
        self.manager= AttendanceManager(db)
        self.username=username
        self.role=role

        root.title("SC Attendance Monitoring")
        root.geometry("900x600")

        self.notebook=ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH,expand=True)
        
        self._build_students_tab()
        self._build_sessions_tab()
        self._build_attendance_tab()
        self._build_reports_tab()
   
    def _build_attendance_tab(self):
        tab=ttk.Frame(self.notebook)
        self.notebook.add(tab,text="Students")

        left =ttk.Frame(tab,padding=10)
        left.pack(side=tk.LEFT, fill=tk.Y)
        right= ttk.Frame(tab,padding=10)
        right.pack(side=tk.RIGHT, fill=tk.BOTH,expand=True)

        ttk.Label(left,text="Student ID").pack()
        self.sid_entry=ttk.Entry(left)
        self.sid_entry.pack()
        ttk.Label(left,text="Name").pack()
        self.sname_entry= ttk.Entry(left)
        self.sname_entry.pack()
        ttk.Label(left,text="Course").pack()
        self.scourse_entry=ttk.Entry(left)
        self.scourse_entry.pack()
        ttk.Label(left,text="Year").pack()
        self.syear_entry=ttk.Entry(left)
        self.syear_entry.pack()

        ttk.Button(left,text="Add/ Update",command=self.add_update_students).pack(pady=5)
        ttk.Button(left,text="Delete",command=self.delete_student).pack(pady=5)
        ttk.Button(left,text="Refresh", command=self.refresh_students).pack(pady=5)

        cols =("student_id","name","course","year")
        self.students_tree= ttk.Treeview(right,columns=cols,show="headings")
        for c in cols:
            self.students_tree.heading(c,text=c.title())
            self.students_tree.column(c,width=150)
            self.students_tree.pack(fill=tk.BOTH,expand=True)
            self.students_tree.bind("<Double-1>",self.on_studeny_select)
    
    def add_update_students(self):
        sid= self.scourse_entry.get().strip()
        name=self.sname_entry.get().strip()
        course=self.scourse_entry.get().strip()
        year=self.syear_entry.get().strip()
        if not sid or not name:
            messagebox.showwarning("Input required", "Student ID and Name required")
            return
            student=Student(student_id=sid,name=name,course=course,year=year)
            self.manager.add_student(student)
            messagebox.showinfo("Saved","Student saved")
            self.refresh_students()

    def delete_student(self):
        sid=self.sid_entry.get().strip()
        if not sid:
                messagebox.showwarning("Select student", "Type or select student id to delete")
                return
        ok=messagebox.askyesno("Delete",f"Delete student{sid}?")
        if ok:
            self.manager.delete_student(sid)
            self.refresh_students()
        
        def refresh_students(self):
         for r in self.students_tree.get_children():
            self.students_tree.delete(r)
        students= self.db.list_students()
        for s in students:
            self.students_tree.insert("",tk.END, values= (s["student_id"],s["name"],s["course"],s["year"]))

    def on_studeny_select(self,event):
        item=self.students_tree.selection()[0]
        vals=self.students_tree.item(item,"values")
        self.sid_entry.delete(0,tk.END);self.sid_entry.insert(0,vals[0])
        self.sname_entry.delete(0,tk.END);self.sname_entry.insert(0,vals[1])
        self.scourse_entry.delete(0,tk.END);self.scourse_entry(0,vals[2])
        self.syear_entry.delete(0,tk.END);self.syear_entry.insert(0,vals[3])
    
    def _build_sessions_tab(self):
        tab=ttk.Frame(self.notebook)
        self.notebook.add(tab,text= "Sessions")

        left=ttk.Frame(tab,padding=10)
        left.pack(side=tk.LEFT,fill=tk.Y)
        right= ttk.Frame(tab,padding=10)
        right.pack(side=tk.RIGHT,fill=tk.BOTH,expand=True)

        ttk.Label(left,text="Subject").pack()
        self.subject_entry=ttk.Entry(left);self.subject_entry.pack()
        ttk.Label(left,text="Schedule").pack()
        self.schedule_entry=ttk.Entry(left);self.schedule_entry.pack()
        ttk.Label(left,text="Section").pack()
        self.section_entry=ttk.Entry(left);self.section_entry.pack()
        ttk.Label(left,text="Section").pack()
        self.instructor_entry=ttk.Entry(left);self.instructor_entry.pack()

        ttk.Button(left,text="Create Session",command=self.create_session).pack(pady=5)
        ttk.Button(left,text="Refesh",command=self.refresh_session).pack(pady=5)
        
        cols= ("session_id", "subject","schedule","section","intructor")
        self.sessions.tree.pack(fill=tk.BOTH,expand=True)
        self.refresh_session()

        def create_session(self):
            subj=self.subject_entry.get().strip()
            sched= self.schedule_entry.get().strip()
            sec=self.section_entry.get().strip()
            instr=self.instructor_entry.get().strip()
            if not subj or not sched:
                messagebox.showwarning("Required","Subjec and Schedule required")
                return
            s= ClassSession(session_id=0,subject= subj,schedule=sched,section=sec,instructor=instr)
            sid=self.db.insert_sessions(s)
            messagebox.showinfo("Saved",f"Session created id={sid}")
            self.refresh_session()
    def refresh_sessions(self):
          for r in self.sessions_tree.get_children():
            self.sessions_tree.delete(r)
          for s in self.db.list_sessions():
            self.sessions_tree.insert("", tk.END, values=(s["session_id"], s["subject"], s["schedule"], s["section"], s["instructor"]))

    def _build_attendance_tab(self):
          tab = ttk.Frame(self.notebook)
          self.notebook.add(tab, text="Attendance")

          top = ttk.Frame(tab, padding=8)
          top.pack(fill=tk.X)
          ttk.Label(top, text="Date (YYYY-MM-DD):").grid(row=0, column=0)
          self.att_date_entry = ttk.Entry(top); self.att_date_entry.grid(row=0, column=1)
          self.att_date_entry.insert(0, datetime.date.today().isoformat())

          ttk.Label(top, text="Session ID:").grid(row=0, column=2)
          self.att_session_entry = ttk.Entry(top); self.att_session_entry.grid(row=0, column=3)
          ttk.Button(top, text="Refresh Students", command=self.refresh_attendance_students).grid(row=0, column=4, padx=5)
          
          body = ttk.Frame(tab, padding=8)
          body.pack(fill=tk.BOTH, expand=True)

          cols = ("student_id","name","status")
          self.att_tree = ttk.Treeview(body, columns=cols, show="headings", selectmode="browse")
          for c in cols:
            self.att_tree.heading(c, text=c.title()); self.att_tree.column(c, width=200)
            self.att_tree.pack(fill=tk.BOTH, expand=True)
            self.refresh_attendance_students()

            bottom = ttk.Frame(tab, padding=8)
            bottom.pack(fill=tk.X)
            ttk.Button(bottom, text="Mark Present", command=lambda:
        self.mark_selected("Present")).pack(side=tk.LEFT, padx=3)
            ttk.Button(bottom, text="Mark Absent", command=lambda:
        self.mark_selected("Absent")).pack(side=tk.LEFT, padx=3)
            ttk.Button(bottom, text="Mark Late", command=lambda:
        self.mark_selected("Late")).pack(side=tk.LEFT, padx=3)
            ttk.Button(bottom, text="Mark Excused", command=lambda:
        self.mark_selected("Excused")).pack(side=tk.LEFT, padx=3)

    def refresh_attendance_students(self):
        for r in self.att_tree.get_children():
            self.att_tree.delete(r)
        students = self.db.list_students()
        for s in students:
          self.att_tree.insert("", tk.END, values=(s["student_id"], s["name"], "Not marked"))

    def mark_selected(self, status):
        sel = self.att_tree.selection()
        if not sel:
          messagebox.showwarning("Select", "Select a student row first")
          return
        row = self.att_tree.item(sel[0], "values")
        student_id = row[0]
        date = self.att_date_entry.get().strip()
        session_id_text = self.att_session_entry.get().strip()
        if not session_id_text.isdigit():
           messagebox.showwarning("Input", "Enter numeric session id")
           return
        session_id = int(session_id_text)
        self.db.insert_attendance(student_id, session_id, date, status, "")
        self.att_tree.set(sel[0], "status", status)
        messagebox.showinfo("Marked", f"{row[1]} marked {status} for session {session_id} on {date}")    
    
    def _build_reports_tab(self):
        tab=ttk.Frame(self.notebook)
        self.notebook.add(tab,text= "Reports")

        frm=ttk.Frame(tab, padding=10);frm.pack(fill=tk.BOTH,expand=True)
        ttk.Label(frm,text="Start Date(YYYY-MM-DD):").grid(row=0,column=1)
        self.r_start=ttk.Entry(frm);self.r_start.grid(row=0,column=1)
        ttk.Label(frm,text="End Date(YYYY-MM-DD):").grid(row=0,column=2)
        self.r_end=ttk.Entry(frm);self.r_end.grid(row=0,column=3)
        ttk.Button(frm,text="Generate Report(Show)",command=self.show_report).grid(row=0,column=5,padx=5)

        cols= ("record_id","student_id","name","date","status","session_id")
        self.report_tree= ttk.Treeview(frm,columns=cols,show="headings")
        for c in cols:
            self.report_tree.heading(c,text=c.title())
            self.report_tree.column(c, width=120)
        self.report_tree.grid(row=1,column=0,columnspan=6,sticky="nsew")
        frm.rowconfigure(1,weight=1)
        frm.columnconfigure(5,weight=1)

    def show_report(self):
        start=self.r_start.grid().strip() or None
        end=self.r_end.grid().strip() or None
        rows= self.db.query_attendance_summary(start,end)
        for r in self.report_tree.get_children:
            self.report_tree.delete(r)
        for r in rows:
            self.report_tree.insert("",tk.END,values=(r.get("record_id"),r.get("student_id"),r.get("name"),r.get("date"),r.get("status"),r.get("session_id")))

    def export_csv(self):
        start = self.r_start.get().strip() or None
        end = self.r_end.get().strip() or None
        rows = self.db.query_attendance_summary(start, end)
        if not rows:
           messagebox.showinfo("No data", "No records to export")
           return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path:
           return
        with open(path, "w", newline="", encoding="utf-8") as f:
         writer = csv.writer(f)
         writer.writerow(["record_id","student_id","name","date","status","session_id"])
        for r in rows:
         writer.writerow([r.get("record_id"), r.get("student_id"), r.get("name"), r.get("date"), r.get("status"), r.get("session_id")])
        messagebox.showinfo("Exported", f"CSV exported to {path}")

    def start_app(root, db, username, role):
        MainApp(root, db, username, role)