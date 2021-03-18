const isEmpty = (obj) =>
  obj && Object.keys(obj).length === 0 && obj.constructor === Object;
const setLocal = (key, value) =>
  localStorage.setItem(key, JSON.stringify(value));

const getLocal = (key, defaultValue = '') => {
  const val = localStorage.getItem(key);

  if (val === null) return defaultValue;

  return JSON.parse(val);
};

const delLocal = (key) => localStorage.removeItem(key);

let inject = (str, obj) => str.replace(/\${(.*?)}/g, (x, g) => obj[g]);

export { isEmpty, setLocal, getLocal, delLocal, inject };
