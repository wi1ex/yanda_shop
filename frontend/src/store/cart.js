import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';
import api from '@/services/api';
import { API } from './apiRoutes';
import { useUserStore } from './user';

export const useCartStore = defineStore('cart', () => {
  // Cart contents
  const cart = ref({ count: 0, total: 0, items: [] });
  const showCart = ref(false);

  // Favorites
  const favorites = ref({ items: [], count: 0 });

  // Dependencies
  const userStore = useUserStore();

  // Reload cart/favorites when user changes
  watch(
    () => userStore.user.id,
    (newId) => {
      if (newId && userStore.isAuthenticated(newId)) {
        loadCartFromServer();
        loadFavoritesFromServer();
      }
    }
  );

  // Actions

  // --- Cart operations ---
  async function loadCartFromServer() {
    if (!userStore.isAuthenticated()) {
      return;
    }

    const userId = userStore.user.id;
    try {
      const { data } = await api.get(API.product.getCart, {
        params: { user_id: userId },
      });
      if (data.items) {
        cart.value.items = data.items;
        cart.value.count = data.count;
        cart.value.total = data.total;
      }
    } catch (e) {
      console.error('Cannot load cart:', e);
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

  async function placeOrder(options = {}) {
    if (!userStore.isAuthenticated()) return null
    try {
      if (!userStore.addresses.length) {
        await userStore.fetchAddresses()
      }
      const primary = userStore.addresses.find(a => a.selected)

      const items = groupedCartItems.value.map(item => ({
        variant_sku:     item.variant_sku,
        world_sku:       item.world_sku,
        price:           item.unit_price,
        qty:             item.quantity,
        delivery_option: item.delivery_option?.label || null,
        image_url:       item.image,
        brand:           item.brand,
        name:            item.name,
        size_label:      item.size_label,
      }))

      function parseMaxDays(label = '') {
        const range = label.match(/(\d+)\D+(\d+)/)
        if (range) return parseInt(range[2], 10)
        const single = label.match(/(\d+)/)
        return single ? parseInt(single[1], 10) : 0
      }
      const maxDays = groupedCartItems.value.reduce((mx, it) => Math.max(mx, parseMaxDays(it.delivery_option?.label)), 0)
      const receiveDate = new Date()
      receiveDate.setDate(receiveDate.getDate() + maxDays)

      const payload = {
        items,
        address_id:     options.address_id ?? undefined,
        payment_method: options.payment_method,
        delivery_type:  options.delivery_type,
        delivery_price: Number(options.delivery_price) || 0,
        delivery_date:  receiveDate.toISOString(),
        first_name:     options.first_name,
        last_name:      options.last_name,
        middle_name:    options.middle_name,
        phone:          options.phone,
        email:          options.email,
      }

      const { data } = await api.post(API.general.createOrder, payload)

      cart.value = { count: 0, total: 0, items: [] }
      deliveryPrice.value = 0
      await saveCartToServer()

      return data.order_id
    } catch (e) {
      console.error('placeOrder error:', e)
      return null
    }
  }

  const groupedCartItems = computed(() => {
    const map = {};
    cart.value.items.forEach((item) => {
      const key = `${item.variant_sku}_${item.delivery_option?.label}`;
      if (!map[key]) {
        map[key] = { ...item, quantity: 0 };
      }
      map[key].quantity++;
    });
    return Object.values(map);
  });

  // --- Favorites operations ---

  async function loadFavoritesFromServer() {
    if (!userStore.isAuthenticated()) {
      return;
    }

    const userId = userStore.user.id;
    try {
      const { data } = await api.get(API.product.getFavorites, {
        params: { user_id: userId },
      });
      favorites.value.items = data.items || [];
      favorites.value.count = data.count || favorites.value.items.length;
    } catch (e) {
      console.error('Cannot load favorites:', e);
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
    cart,
    showCart,
    openCartDrawer,
    closeCartDrawer,
    addToCart,
    increaseQuantity,
    decreaseQuantity,
    getProductQuantity,
    placeOrder,
    groupedCartItems,

    // Favorites state & actions
    favorites,
    loadFavoritesFromServer,
    addToFavorites,
    removeFromFavorites,
    isFavorite,
  };
});
