from pyscript import when, document

@when("click", "#submit-btn")
def on_submit(event):
    text = document.querySelector("#user-text").value
    print(text)