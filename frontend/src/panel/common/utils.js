const isString = (string) =>
  Object.prototype.toString.call(string) === '[object String]';

const getObj = (error) => {
  if (
    error &&
    error.response &&
    error.response.data &&
    error.response.data.detail
  )
    return error.response.data.detail;
  else if (error && error.response && error.response.data)
    return error.response.data;
  else {
    const isObj = error.toString().startsWith('[object');
    if (isObj) return 'An error occurred.';
    else return error.toString();
  }
};

const getError = (error) => {
  let result = getObj(error);
  console.log(result);
  if (isString(result)) {
    if (result.length < 200) return result;
    else console.log(result);
  } else {
    const json = JSON.stringify(result);
    if (json !== '{}') return json;
  }
  return 'An error occured';
};

export { getError };
