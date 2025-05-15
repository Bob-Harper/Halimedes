import time
# import stuff
# NOT USED YET.  EXAMPLE PLACEHOLDER
# See Stygia database/prompt handling for examples and ideas on how to implement.

class MemoryHandler:
    def __init__(self, db_interface):
        self.db = db_interface

    def remember_face(self, face_embedding, user_name=None):
        entry = {
            'type': 'face',
            'user_name': user_name,
            'embedding': face_embedding,
            'timestamp': time.time()
        }
        self.db.save(entry)

    def remember_voice(self, voice_embedding, user_name=None):
        entry = {
            'type': 'voice',
            'user_name': user_name,
            'embedding': voice_embedding,
            'timestamp': time.time()
        }
        self.db.save(entry)

    def retrieve_by_similarity(self, embedding, threshold=0.75):
        # returns closest matches above threshold
        return self.db.search(embedding, threshold=threshold)
