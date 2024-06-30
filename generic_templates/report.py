class Report():
    def __init__(self, textwidth=80):
        self.sections = []
        self.sections_log = {}
        self.attachments = {}
        self.textwidth = textwidth
        self.section("Overview")
        self.pending_subhead = None

    def section(self, section):
        self.current_section = section
        if not section in self.sections:
            self.sections.append(section)
            self.sections_log[section] = []

    def attach(self, name, value):
        self.attachments[name] = value
        self.print(f"    See attachment: '{name}'")

    def attachment(self, name):
        return self.attachments[name]

    def has_attachment(self, name):
        return name in self.attachments

    def log_text(self, txt):
        #if txt == "" and len(self.sections_log[self.current_section])==0: return
        if len(txt)>self.textwidth: txt=txt[:self.textwidth-3]+"..."
        self.sections_log[self.current_section].append(txt)

    def sub_heading(self, header):
        self.pending_subhead = header
        
    def sub_section(self, header):
        self.pending_subhead = header

    def print(self, *data):
        if not self.pending_subhead is None:
            self.log_text("")
            self.log_text("  \u2022 " + self.pending_subhead)
            self.pending_subhead = None
        #print("data=",data)
        self.log_text("    "+(" ".join([str(x) for x in data])))

    def __str__(self):
        result = ""
        for i in range(len(self.sections)):
            if i>0: result += "\n"
            section = self.sections[i]
            result += f"{i+1}. {section}\n"
            for j in range(len(self.sections_log[section])):
                result += f"{self.sections_log[section][j]}\n"
        return result

    def show(self):
        print(str(self))
