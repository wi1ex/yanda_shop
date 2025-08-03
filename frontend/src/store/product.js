import { defineStore } from 'pinia';
import { ref, reactive, computed, watch } from 'vue';
import api from '@/services/api';
import { API } from './apiRoutes';

export const useProductStore = defineStore('product', () => {
  // State
  const categoryList = ref(['Одежда', 'Обувь', 'Аксессуары']);
  const selectedCategory = ref('');
  const showSubcats = ref(false);
  const selectedSubcat = ref('');
  const currentSubcatPage = ref(0);
  const isFetching = ref(false);

  const sortBy = ref('date');
  const sortOrder = ref('desc');

  const filterPriceMin = ref(null);
  const filterPriceMax = ref(null);
  const filterGender = ref('');
  const filterSubcat = ref('');
  const filterBrands = ref([]);
  const filterColors = ref([]);
  const filterSizes = ref([]);

  const products = ref([]);
  const detailData = ref(null);
  const detailLoading = ref(false);
  const variants = ref([]);

  // Grouping indices
  const colorGroups = ref([]);
  const distinctBrands = ref([]);
  const distinctColors = ref([]);
  const distinctSizes = ref([]);
  const indexByField = reactive({
    category: new Map(),
    subcat: new Map(),
    gender: new Map(),
    brand: new Map(),
    color: new Map(),
    size: new Map()
  });

  // Computed
  const subcatListMap = computed(() => {
    const map = {
      'Одежда': new Set(),
      'Обувь': new Set(),
      'Аксессуары': new Set()
    };
    products.value.forEach(p => {
      if (filterGender.value && p.gender !== filterGender.value && p.gender !== 'U') return;
      if (!map[p.category]) return;
      map[p.category].add(p.subcategory);
    });
    return Object.fromEntries(
      Object.entries(map).map(([k, s]) => [k, Array.from(s).sort()])
    );
  });

  function intersect(a, b) {
    return new Set([...a].filter(x => b.has(x)));
  }

  function union(a, b) {
    b.forEach(x => a.add(x));
    return a;
  }

  const displayedProducts = computed(() => {
    let result = new Set(colorGroups.value);

    if (selectedCategory.value) {
      result = intersect(
        result,
        indexByField.category.get(selectedCategory.value) || new Set()
      );
    }

    if (filterSubcat.value) {
      result = intersect(
        result,
        indexByField.subcat.get(filterSubcat.value) || new Set()
      );
    }

    if (['M', 'F'].includes(filterGender.value)) {
      const byG = indexByField.gender.get(filterGender.value) || new Set();
      const byU = indexByField.gender.get('U') || new Set();
      const allG = new Set(byG);
      byU.forEach(x => allG.add(x));
      result = intersect(result, allG);
    }

    if (filterBrands.value.length) {
      const u = filterBrands.value
        .map(b => indexByField.brand.get(b) || new Set())
        .reduce(union, new Set());
      result = intersect(result, u);
    }

    if (filterColors.value.length) {
      const u = filterColors.value
        .map(c => indexByField.color.get(c) || new Set())
        .reduce(union, new Set());
      result = intersect(result, u);
    }

    if (filterSizes.value.length) {
      const u = filterSizes.value
        .map(s => indexByField.size.get(s) || new Set())
        .reduce(union, new Set());
      result = intersect(result, u);
    }

    if (filterPriceMin.value != null) {
      result = new Set(
        [...result].filter(g =>
          g.variants.some(v => v.price >= filterPriceMin.value)
        )
      );
    }

    if (filterPriceMax.value != null) {
      result = new Set(
        [...result].filter(g =>
          g.variants.some(v => v.price <= filterPriceMax.value)
        )
      );
    }

    const arr = Array.from(result);
    arr.forEach(g => {
      g.totalSales = g.variants.reduce((sum, v) => sum + (v.count_sales || 0), 0);
      const minP = g.variants.reduce((p, c) => (p.price <= c.price ? p : c));
      g.minPriceVariant = minP;
      g.minPrice = minP.price;
      const minD = g.variants.reduce((p, c) =>
        p.created_at <= c.created_at ? p : c
      );
      g.minDateVariant = minD;
      g.minDate = minD.created_at;
    });

    const mod = sortOrder.value === 'asc' ? 1 : -1;
    if (sortBy.value === 'price') {
      arr.sort((a, b) => mod * (a.minPrice - b.minPrice));
    } else if (sortBy.value === 'sales') {
      arr.sort(
        (a, b) => mod * (a.totalSales - b.totalSales) || mod * (a.minPrice - b.minPrice)
      );
    } else {
      arr.sort((a, b) => mod * a.minDate.localeCompare(b.minDate));
    }

    return arr;
  });

  // Actions

  function buildIndexes(list) {
    const groups = {};
    list.forEach(p => {
      if (!groups[p.color_sku]) {
        groups[p.color_sku] = { color_sku: p.color_sku, variants: [] };
      }
      groups[p.color_sku].variants.push(p);
    });
    const all = Object.values(groups);
    all.forEach(g => {
      g.minPriceVariant = g.variants.reduce((prev, cur) => prev.price <= cur.price ? prev : cur);
    });
    colorGroups.value = all;

    // reset indices
    Object.values(indexByField).forEach(m => m.clear());

    const add = (map, key, group) => {
      if (!map.has(key)) map.set(key, new Set());
      map.get(key).add(group);
    };

    all.forEach(g => {
      new Set(g.variants.map(v => v.category)).forEach(cat =>
        add(indexByField.category, cat, g)
      );
      new Set(g.variants.map(v => v.subcategory)).forEach(sc =>
        add(indexByField.subcat, sc, g)
      );
      new Set(g.variants.map(v => v.gender)).forEach(gd =>
        add(indexByField.gender, gd, g)
      );
      new Set(g.variants.map(v => v.brand)).forEach(br =>
        add(indexByField.brand, br, g)
      );
      new Set(g.variants.map(v => v.color)).forEach(cl =>
        add(indexByField.color, cl, g)
      );
      new Set(g.variants.map(v => v.size_label)).forEach(sz =>
        add(indexByField.size, sz, g)
      );
    });

    distinctBrands.value = Array.from(indexByField.brand.keys()).sort((a, b) =>
      a.localeCompare(b, 'ru')
    )

    distinctColors.value = Array.from(indexByField.color.keys()).sort((a, b) =>
      a.localeCompare(b, 'ru')
    )

    const letterRe = /^[A-Za-z]+$/;
    const numericRe = /^\d+(\.\d+)?$/;
    const letterOrder = ['XXXXS','XXXS','XXS','XS','S','M','L','XL','XXL','XXXL','XXXXL'];

    distinctSizes.value = Array.from(indexByField.size.keys())
      .sort((a, b) => {
        const aIsLetter = letterRe.test(a);
        const bIsLetter = letterRe.test(b);
        if (aIsLetter && bIsLetter) {
          const ai = letterOrder.indexOf(a);
          const bi = letterOrder.indexOf(b);
          if (ai !== -1 && bi !== -1) return ai - bi;
          if (ai !== -1) return -1;
          if (bi !== -1) return 1;
          return a.localeCompare(b, 'ru', { sensitivity: 'base' });
        }
        if (aIsLetter) return -1;
        if (bIsLetter) return 1;

        const aIsNum = numericRe.test(a);
        const bIsNum = numericRe.test(b);
        if (aIsNum && bIsNum) {
          return parseFloat(a) - parseFloat(b);
        }
        if (aIsNum) return -1;
        if (bIsNum) return 1;
        return a.localeCompare(b, 'ru', { sensitivity: 'base' });
      });
  }

  async function fetchProducts() {
    if (isFetching.value) return;
    isFetching.value = true;
    try {
      const { data } = await api.get(API.product.listProducts);
      products.value = data;
      buildIndexes(data);
    } catch (e) {
      console.error('Failed to load products:', e);
    } finally {
      isFetching.value = false;
    }
  }

  async function fetchDetail(variantSku, category) {
    detailLoading.value = true;
    try {
      const { data } = await api.get(API.product.getProduct, {
        params: { category, variant_sku: variantSku }
      });
      detailData.value = data;
      await fetchProducts();
      variants.value = products.value.filter(p => p.sku === data.sku);
    } catch (e) {
      console.error('Failed to load product detail:', e);
    } finally {
      detailLoading.value = false;
    }
  }

  function changeCategory(cat) {
    selectedCategory.value = cat;
    sortBy.value = 'date';
    sortOrder.value = 'desc';
    clearFilters();
  }

  function openSubcats() {
    selectedSubcat.value = '';
    currentSubcatPage.value = 0;
    showSubcats.value = true;
  }

  function backToCats() {
    showSubcats.value = false;
    selectedSubcat.value = '';
    filterSubcat.value = '';
    currentSubcatPage.value = 0;
    selectedCategory.value = '';
  }

  function pickSubcat(sc) {
    if (selectedSubcat.value === sc) {
      selectedSubcat.value = '';
      filterSubcat.value = '';
    } else {
      selectedSubcat.value = sc;
      filterSubcat.value = sc;
    }
  }

  function clearFilters() {
    filterPriceMin.value = null;
    filterPriceMax.value = null;
    filterSubcat.value = '';
    filterGender.value = '';
    filterBrands.value = [];
    filterColors.value = [];
    filterSizes.value = [];
  }

  watch(filterGender.value, () => {
    showSubcats.value = false
    selectedSubcat.value = ''
    currentSubcatPage.value = 0
  })

  return {
    // State
    categoryList,
    selectedCategory,
    showSubcats,
    selectedSubcat,
    currentSubcatPage,
    isFetching,
    sortBy,
    sortOrder,
    filterPriceMin,
    filterPriceMax,
    filterGender,
    filterSubcat,
    filterBrands,
    filterColors,
    filterSizes,
    products,
    detailData,
    detailLoading,
    variants,

    // Grouping & computed
    colorGroups,
    distinctBrands,
    distinctColors,
    distinctSizes,
    indexByField,
    subcatListMap,
    displayedProducts,

    // Actions
    fetchProducts,
    fetchDetail,
    buildIndexes,
    changeCategory,
    openSubcats,
    backToCats,
    pickSubcat,
    clearFilters
  };
});
