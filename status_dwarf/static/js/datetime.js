// Replace ISO UTC datetime with user timezone datetime
document.querySelectorAll(".datetime").forEach(function (element) {
    const utcDate = new Date(element.innerHTML.trim())
    const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const userLanguage = navigator.language || 'en-US';
    const options = {
        timeZone: userTimezone,
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        hour12: false,
        minute: '2-digit',
    }
    element.innerHTML = utcDate.toLocaleString(userLanguage, options)
})
