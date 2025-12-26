<template>
  <nav class="navbar">
    <div class="navbar-brand">
      <span class="brand-icon">🌍</span>
      <h1>PreDis</h1>
    </div>
    <div class="navbar-links">
      <a href="#" class="nav-link">Sobre</a>
      <a href="#" class="nav-link">Contato</a>
    </div>
  </nav>
</template>

<script setup>
// Nenhuma lógica de script necessária para este componente simples por enquanto.
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #ffffff;
  padding: 0.5rem 2rem;
  border-bottom: 1px solid #e0e0e0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.navbar-brand {
  display: flex;
  align-items: center;
}

.navbar-brand h1 {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--primary-green, #007A33);
  margin: 0;
  margin-left: 0.5rem;
}

.brand-icon {
  font-size: 1.5rem;
}

.navbar-links {
  display: flex;
  gap: 1.5rem;
}

.nav-link {
  text-decoration: none;
  color: #555;
  font-weight: 400;
  transition: color 0.3s ease;
}

.nav-link:hover {
  color: var(--primary-green, #007A33);
}
</style>
