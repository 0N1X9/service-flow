const html = document.documentElement;
const themes = ["light", "dark", "system"];
const icons = {
    light: "☀️",
    dark: "🌙",
    system: "💻",
};

document.addEventListener("DOMContentLoaded", () => {
    const button = document.getElementById("theme-toggle");
    let theme = localStorage.getItem("theme") || "system";
    // Enable line if base.html script is disabled
    // applyTheme(theme);
    updateButton(button, theme);
    button.addEventListener("click", () => {
        let index = themes.indexOf(theme);
        theme = themes[(index + 1) % themes.length];
        localStorage.setItem("theme", theme);
        applyTheme(theme);
        updateButton(button, theme);
    });
});

function updateButton(button, theme) {
    button.textContent = icons[theme];
}

function applyTheme(theme) {
    if (theme === "light") {
        html.setAttribute("data-theme", "light");
        return;
    }

    if (theme === "dark") {
        html.setAttribute("data-theme", "dark");
        return;
    }

    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    html.setAttribute("data-theme", prefersDark ? "dark" : "light");
}