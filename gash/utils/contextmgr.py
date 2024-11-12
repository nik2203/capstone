class SessionContext:
    def __init__(self, max_history_length=20):
        """
        Initialize the session context with an optional max history length.
        """
        self.history = []
        self.personality = None  # Store personality here
        self.max_history_length = max_history_length  # Limit the size of history for memory efficiency

    def add_to_history(self, command, response):
        """
        Add a command-response pair to the session history.
        Ensures the history does not exceed the maximum length.
        """
        self.history.append({"command": command, "response": response})
        if len(self.history) > self.max_history_length:
            self.history.pop(0)  # Remove the oldest entry to maintain the size limit

    def get_context(self):
        """
        Generate the current session context as a string.
        Only the most recent entries (up to max_history_length) are included.
        """
        return "\n".join(
            f"Command: {entry['command']}, Response: {entry['response']}" for entry in self.history
        )

    def set_personality(self, personality):
        """
        Set the system's personality for the session.
        """
        self.personality = personality

    def has_personality(self):
        """
        Check if a personality has been set.
        """
        return self.personality is not None

    def get_personality(self):
        """
        Retrieve the stored personality.
        If none is set, return an empty string.
        """
        return self.personality if self.personality else ""

    def reset_context(self):
        """
        Reset the session context by clearing history and personality.
        """
        self.history = []
        self.personality = None
