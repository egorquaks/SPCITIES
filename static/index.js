const isAuthed = document.getElementById("app").getAttribute("is-authed") === "True"

const deleteCookieAndReload = (cookieName) => {
    document.cookie = cookieName + "=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    location.reload()
};