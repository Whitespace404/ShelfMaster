
const selectField = document.getElementById("type");
const userInputBox = document.getElementById("hide-inputs");

selectField.addEventListener("change", function () {
    if (selectField.value === "Book") {
        userInputBox.classList.remove("hidden");
    } else {
        userInputBox.classList.add("hidden");
    }
});
