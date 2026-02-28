from rag.retriever import CropRetriever


class FarmerAssistant:
    def __init__(self):
        self.retriever = CropRetriever()

    def answer(self, question):
        question_lower = question.lower()

        # Step 1: detect crop from metadata list
        all_crops = list(set([m["crop"] for m in self.retriever.metadata]))

        selected_crop = None
        for crop in all_crops:
            if crop in question_lower:
                selected_crop = crop
                break

        # fallback to retrieval if crop not found directly
        if not selected_crop:
            results = self.retriever.search(question, top_k=5)
            if results:
                selected_crop = results[0]["crop"]
            else:
                return "Sorry, I could not detect the crop."

        # Step 2: detect section intent
        section_keywords = {
            "Climate": ["climate", "temperature", "temp", "rainfall", "weather"],
            "Plant protection": ["disease", "pest"],
            "Fertilizer": ["fertilizer", "manure"],
            "Irrigation": ["irrigation", "water"],
            "Soil": ["soil", "ph"],
        }

        target_section = None
        for section, keywords in section_keywords.items():
            for word in keywords:
                if word in question_lower:
                    target_section = section
                    break
            if target_section:
                break

        # Step 3: Direct metadata filtering
        for chunk in self.retriever.metadata:
            if chunk["crop"] == selected_crop:
                if target_section and target_section.lower() in chunk["section"].lower():
                    return f"{selected_crop.upper()} - {chunk['section']}\n\n{chunk['content']}"

        # fallback to first chunk of crop
        for chunk in self.retriever.metadata:
            if chunk["crop"] == selected_crop:
                return f"{selected_crop.upper()}\n\n{chunk['content']}"

        return "Sorry, I could not find relevant information."


if __name__ == "__main__":
    assistant = FarmerAssistant()

    while True:
        question = input("\nAsk your farming question: ")
        print("\nAnswer:\n")
        print(assistant.answer(question))