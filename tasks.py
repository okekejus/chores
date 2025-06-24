class Chore: 
    def __init__(self, section): 
        self.section = section
        self.tasks = []
        self.freq = str()
    
    def add_tasks(self, tasks): 
        for task in tasks: 
            self.tasks.append(task)

    def add_freq(self, freq): 
        self.freq = freq


# Kitchen 
kitchen = Chore("Kitchen")
kitchen.add_tasks(["Sweep + mop floors", "Wipe down appliances (Fridge, Microwave)", "Wipe counters and other surfaces", "Wash dish drying cushion", "Throw out moldy/expired food", "Empty bins + replace bags"])
kitchen.add_freq("Weekly")

# Dining 
dining = Chore("Dining")
dining.add_freq("Weekly")
dining.add_tasks(["Sweep + Mop + Vacuum rugs", "Wipe tables + surfaces", "Empty bins", "Fold blankets", "Re-house random items"])

# Landing 
landing = Chore("Landing")
landing.add_freq("Weekly")
landing.add_tasks(["Sweep + Mop + Vacuum Floors", "Scrub toilet bowl/areas", "Empty trash", "Scrub tub", "Wash Shower mat"])
