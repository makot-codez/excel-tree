import pandas as pd
import json

# load JSON data from a file
with open('data.json') as f:
    data = json.load(f)

# JSON data separated by comma
data2 = {
  "ID": ["1", "2", "3", "1.1", "1.1.1", "1.1", "1"],
  "Name": ["Root1", "Root2", "Root3", "Child1", "GrandChild1", "Another Child1", "Another Root1"],
  "Category": ["A", "A", "A", "A", "A", "B", "B"]
}
# create DataFrame
df = pd.DataFrame(data)
print(df)

# split the ID column into three columns
df[['Level1', 'Level2', 'Level3']] = df['ID'].str.split('.', expand=True)
print(df)

# make parent ID
df['ParentID'] = df.apply(lambda row: '.'.join(row['ID'].split('.')[:-1]), axis=1)
# if the parent ID is empty, fill it with 'Root'
df['ParentID'] = df['ParentID'].replace('', 'Root')
print(df)

# build tree structure drom parent-child relationship
def build_tree(df, parent_id, category=None):
  tree = []
  if category:
    childen = df[(df['ParentID'] == parent_id) & (df['Category'] == category)]
  else:
    childen = df[df['ParentID'] == parent_id]

  for _, row in childen.iterrows():
    # check if duplicate children ID
    existing_node = next((node for node in tree if node['ID'] == row['ID']), None)
    if existing_node:
      existing_node['Children'].extend(build_tree(df, row['ID'], row['Category']))
    else:
#      node = row.to_dict()
#      node['Children'] = build_tree(df, row['ID'])
      node = {
        'ID': row['ID'],
        'Name': row['Name'],
        'Children': build_tree(df, row['ID'], row['Category'])
      }
      tree.append(node)
  return tree

# build tree by category
tree_by_category = {}
# catgoris from unique DataFrame Category
categories = df['Category'].unique()
for category in categories:
  tree_by_category[category] = build_tree(df, 'Root', category)

# build tree from the root
trees_json = json.dumps(tree_by_category, indent=2, ensure_ascii=False)
print(trees_json)