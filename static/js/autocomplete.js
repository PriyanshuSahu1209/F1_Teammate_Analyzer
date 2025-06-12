document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("driver-input");
  const datalist = document.getElementById("driver-suggestions");

  input.addEventListener("input", async () => {
    const query = input.value.trim();
    if (query.length < 2) return;

    try {
      const res = await fetch(`/autocomplete?q=${encodeURIComponent(query)}`);
      if (!res.ok) throw new Error("Failed to fetch");
      const names = await res.json();

      datalist.innerHTML = "";
      names.forEach(name => {
        const option = document.createElement("option");
        option.value = name;
        datalist.appendChild(option);
      });
    } catch (err) {
      console.error("Autocomplete error:", err);
    }
  });
});
