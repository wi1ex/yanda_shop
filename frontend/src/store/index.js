// src/store/index.js
import { useProductStore } from './product';
import { useCartStore }    from './cart';
import { useUserStore }    from './user';
import { useAdminStore }   from './admin';
import { API }             from './apiRoutes';

export function useStore() {
  const prod = useProductStore()
  const cart = useCartStore()
  const user = useUserStore()
  const admin= useAdminStore()
  return {
    ...prod,
    ...cart,
    ...user,
    ...admin,
    api: API,
  }
}
