<h1>Work Log Database</h1>

<h2>Table of Contents</h2>
<ol>
  <li><a href="#description">Description</a></li>
  <li><a href="#installation">Installation</a></li>
</ol>

<h2 id="description">1. Description</h2>
<p>I developed a terminal application to prepare better work timesheets. The program asks for a name, date, task name, time spent on the task, and optional notes. Each task gets added to a database. Users can also view, edit, and delete previously added entries. I also wrote several unit tests to check that the code does what I expect.</p>

<table>
  <tr>
    <th>Main Menu</th>
    <th>Add New Entry</th>
  </tr>
  <tr>
    <td><img src="assets/main_menu.png" width=500></td>
    <td><img src="assets/add_entry.png" width=500></td>
  </tr>
  <tr>
    <th>View Previous Entries</th>
    <th>Results</th>
  </tr>
  <tr>
    <td><img src="assets/view_entries.png" width=500></td>
    <td><img src="assets/results.png" width=500></td>
  </tr>
</table>

<h2 id="installation">Installation</h2>

```
git clone https://github.com/marcusvanwinden/work_log_db.git
cd work_log_db
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
python3 app.py
```
