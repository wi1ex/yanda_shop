import { useProductStore } from './product';
import { useCartStore }    from './cart';
import { useUserStore }    from './user';
import { useAdminStore }   from './admin';
import { useGlobalStore }  from './global'
import { API }             from './apiRoutes';

export function useStore() {
  return {
    productStore:  useProductStore(),
    cartStore:     useCartStore(),
    userStore:     useUserStore(),
    adminStore:    useAdminStore(),
    globalStore:   useGlobalStore(),
    apiStore:      API,
  }
}
