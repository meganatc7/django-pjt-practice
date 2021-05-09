const searchField = document.querySelector('#search-field');

const tableOutput = document.querySelector('.table-output');
const appTable = document.querySelector('.app-table');
const paginationContainer = document.querySelector('.pagination-container')
const tBody = document.querySelector('.table-body')

tableOutput.style.display = 'none';

searchField.addEventListener('input',(e) => {
  const searchValue = e.target.value;

  if (searchValue.trim().length > 0) {
    paginationContainer.style.display = 'none';
    tBody.innerHTML = '';
    fetch('/search-expenses/', {
      body: JSON.stringify({ searchText: searchValue}),
      method: "POST",
    })
      .then((res) => res.json())
      .then((data) => {
        
        appTable.style.display = 'none';
        tableOutput.style.display = 'block';


        if (data.length === 0) {
          tableOutput.innerHTML = 'No results found'
        } else {

          data.forEach((item) => {
            tBody.innerHTML += `
              <tr>
                <td>${item.amount}</td>
                <td>${item.category}</td>
                <td>${item.description}</td>
                <td>${item.date}</td>
              </tr>
            `
          })
        }
      })
  } else {
    tableOutput.style.display = 'none';
    appTable.style.display = 'block';
    paginationContainer.style.display = 'block';
  }
})