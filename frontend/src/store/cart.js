import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';
import api from '@/services/api';
import { API } from './apiRoutes';
import { useUserStore } from './user';

export const useCartStore = defineStore('cart', () => {
  // Cart contents
  const cartOrder = ref([]);
  const cart = ref({ count: 0, total: 0, items: [] });
  const cartLoaded = ref(false);
  const showCart = ref(false);

  // Favorites
  const favorites = ref({ items: [], count: 0 });
  const favoritesLoaded = ref(false);

  // Dependencies
  const userStore = useUserStore();

  // Reload cart/favorites when user changes
  watch(
    () => userStore.user.id,
    (newId) => {
      if (newId && userStore.isAuthenticated(newId)) {
        loadCartFromServer();
        loadFavoritesFromServer();
      } else {
        cartLoaded.value = true;
        favoritesLoaded.value = true;
      }
    }
  );

  // Actions

  // --- Cart operations ---

  async function loadCartFromServer() {
    const userId = userStore.user.id;
    if (!userStore.isAuthenticated()) {
      cartLoaded.value = true;
      return;
    }

    try {
      const { data } = await api.get(API.product.getCart, {
        params: { user_id: userId },
      });
      if (data.items) {
        cart.value.items = data.items;
        cart.value.count = data.count;
        cart.value.total = data.total;
        cartOrder.value = Array.from(
          new Set(data.items.map((i) => i.variant_sku))
        );
      }
    } catch (e) {
      console.error('Cannot load cart:', e);
    } finally {
      cartLoaded.value = true;
    }
  }

  async function saveCartToServer() {
    const userId = userStore.user.id;
    if (!userStore.isAuthenticated()) return;

    const payload = {
      user_id: userId,
      items: cart.value.items.map((i) => ({
        variant_sku: i.variant_sku,
        delivery_label: i.delivery_option?.label || null,
      })),
    };

    try {
      await api.post(API.product.saveCart, payload);
    } catch (e) {
      console.error('Error saving cart:', e);
    }
  }

  function openCartDrawer() {
    showCart.value = true;
  }

  function closeCartDrawer() {
    showCart.value = false;
  }

  function addToCart(product) {
    const unitPrice = product.computed_price ?? product.price;
    const existing = cart.value.items.find(
      (i) =>
        i.variant_sku === product.variant_sku &&
        i.delivery_option?.label === product.delivery_option?.label
    );

    if (existing) {
      increaseQuantity(existing);
    } else {
      cart.value.count++;
      cart.value.total += unitPrice;
      const id = `${Date.now()}-${Math.random()}`;
      cart.value.items.push({ ...product, id, unit_price: unitPrice });
      cartOrder.value.push(product.variant_sku);
    }

    saveCartToServer();
  }

  function increaseQuantity(item) {
    cart.value.count++;
    cart.value.total += item.unit_price;
    cart.value.items.push(item);
    saveCartToServer();
  }

  function decreaseQuantity(product) {
    const idx = cart.value.items.findIndex(
      (i) =>
        i.variant_sku === product.variant_sku &&
        i.delivery_option?.label === product.delivery_option?.label
    );
    if (idx < 0) return;

    const sameCount = cart.value.items.filter(
      (i) =>
        i.variant_sku === product.variant_sku &&
        i.delivery_option?.label === product.delivery_option?.label
    ).length;

    cart.value.count--;
    const delta = product.unit_price ?? product.price;
    cart.value.total = Math.max(cart.value.total - delta, 0);

    if (sameCount > 1) {
      cart.value.items.splice(idx, 1);
    } else {
      cart.value.items = cart.value.items.filter(
        (i) =>
          !(
            i.variant_sku === product.variant_sku &&
            i.delivery_option?.label === product.delivery_option?.label
          )
      );
      cartOrder.value = cartOrder.value.filter(
        (sku) => sku !== product.variant_sku
      );
    }

    saveCartToServer();
  }

  function getProductQuantity(product) {
    return cart.value.items.filter(
      (i) =>
        i.variant_sku === product.variant_sku &&
        i.delivery_option?.label === product.delivery_option?.label
    ).length;
  }

  function checkout() {
    cart.value = { count: 0, total: 0, items: [] };
    cartOrder.value = [];
    saveCartToServer();
  }

  const groupedCartItems = computed(() => {
    const map = {};
    cart.value.items.forEach((item) => {
      const key = `${item.variant_sku}_${item.delivery_option?.label}`;
      if (!map[key]) {
        map[key] = { ...item, quantity: 0, totalPrice: 0 };
      }
      map[key].quantity++;
      map[key].totalPrice += item.price;
    });
    return Object.values(map);
  });

  // --- Favorites operations ---

  async function loadFavoritesFromServer() {
    const userId = userStore.user.id;
    if (!userStore.isAuthenticated()) {
      favoritesLoaded.value = true;
      return;
    }

    try {
      const { data } = await api.get(API.product.getFavorites, {
        params: { user_id: userId },
      });
      favorites.value.items = data.items || [];
      favorites.value.count = data.count || favorites.value.items.length;
    } catch (e) {
      console.error('Cannot load favorites:', e);
    } finally {
      favoritesLoaded.value = true;
    }
  }

  async function saveFavoritesToServer() {
    const userId = userStore.user.id;
    if (!userStore.isAuthenticated()) return;

    const payload = {
      user_id: userId,
      items: favorites.value.items,
    };

    try {
      await api.post(API.product.saveFavorites, payload);
    } catch (e) {
      console.error('Error saving favorites:', e);
    }
  }

  function addToFavorites(colorSku) {
    if (!favorites.value.items.includes(colorSku)) {
      favorites.value.items.push(colorSku);
      favorites.value.count = favorites.value.items.length;
      saveFavoritesToServer();
    }
  }

  function removeFromFavorites(colorSku) {
    favorites.value.items = favorites.value.items.filter((cs) => cs !== colorSku);
    favorites.value.count = favorites.value.items.length;
    saveFavoritesToServer();
  }

  function isFavorite(colorSku) {
    return favorites.value.items.includes(colorSku);
  }

  return {
    // Cart state & actions
    cartOrder,
    cart,
    cartLoaded,
    showCart,
    openCartDrawer,
    closeCartDrawer,
    addToCart,
    increaseQuantity,
    decreaseQuantity,
    getProductQuantity,
    checkout,
    groupedCartItems,

    // Favorites state & actions
    favorites,
    favoritesLoaded,
    loadFavoritesFromServer,
    addToFavorites,
    removeFromFavorites,
    isFavorite,
  };
});
