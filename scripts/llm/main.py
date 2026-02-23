from selene import Selene

if __name__ == "__main__":
    selene = Selene()

    while True:
        user = input("You: ")
        if user.lower() in {"exit", "quit"}:
            break

        output = selene.handle_input(user)
        print("Selene: ", output["speech"])
        print("Intent: ", output["intent"])
        print("Gesture: ", output["gesture"])
