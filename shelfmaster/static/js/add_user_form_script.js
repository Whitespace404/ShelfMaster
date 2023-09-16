
const selectField = document.getElementById("is_teacher");
const userInputBox = document.getElementById("hide-inputs");

selectField.addEventListener("change", function () {
    if (selectField.value === "Student") {
        userInputBox.classList.remove("hidden");
    } else {
        userInputBox.classList.add("hidden");
    }
});
