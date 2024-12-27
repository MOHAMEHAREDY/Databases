#!/bin/bash

DB_PATH="./databases"

# Ensure database directory exists
mkdir -p $DB_PATH

# Main Menu Function
function main_menu() {
    echo "===================="
    echo "1. Create Database"
    echo "2. List Databases"
    echo "3. Connect to Database"
    echo "4. Drop Database"
    echo "5. Rename Database"
    echo "6. Exit"
    echo "===================="
    read -p "Enter your choice: " choice
    case $choice in
        1) create_database ;;
        2) list_databases ;;
        3) connect_database ;;
        4) drop_database ;;
        5) rename_database ;;
        6) exit 0 ;;
        *) echo "Invalid choice"; main_menu ;;
    esac
}

# Create Database
function create_database() {
    read -p "Enter database name: " dbname
    if [ -d "$DB_PATH/$dbname" ]; then
        echo "Database already exists!"
    else
        mkdir "$DB_PATH/$dbname"
        echo "Database created."
    fi
    main_menu
}

# List Databases
function list_databases() {
    echo "Databases:"
    ls $DB_PATH
    main_menu
}

# Connect to Database
function connect_database() {
    read -p "Enter database name to connect: " dbname
    if [ -d "$DB_PATH/$dbname" ]; then
        cd "$DB_PATH/$dbname"
        database_menu
    else
        echo "Database does not exist!"
        main_menu
    fi
}

# Drop Database
function drop_database() {
    read -p "Enter database name to drop: " dbname
    if [ -d "$DB_PATH/$dbname" ]; then
        rm -r "$DB_PATH/$dbname"
        echo "Database dropped."
    else
        echo "Database does not exist!"
    fi
    main_menu
}

# Rename Database
function rename_database() {
    read -p "Enter current database name: " current_db
    if [ ! -d "$DB_PATH/$current_db" ]; then
        echo "Database does not exist!"
    else
        read -p "Enter new database name: " new_db
        if [ -d "$DB_PATH/$new_db" ]; then
            echo "A database with the new name already exists!"
        else
            mv "$DB_PATH/$current_db" "$DB_PATH/$new_db"
            echo "Database renamed successfully."
        fi
    fi
    main_menu
}

# Database Menu Function
function database_menu() {
    echo "===================="
    echo "1. Create Table"
    echo "2. List Tables"
    echo "3. Drop Table"
    echo "4. Insert Into Table"
    echo "5. Select From Table"
    echo "6. Delete From Table"
    echo "7. Update Table"
    echo "8. Back to Main Menu"
    echo "===================="
    read -p "Enter your choice: " choice
    case $choice in
        1) create_table ;;
        2) list_tables ;;
        3) drop_table ;;
        4) insert_into_table ;;
        5) select_from_table ;;
        6) delete_from_table ;;
        7) update_table ;;
        8) cd $DB_PATH; main_menu ;;
        *) echo "Invalid choice"; database_menu ;;
    esac
}

# Create Table
function create_table() {
    read -p "Enter table name: " tablename
    if [ -f "$tablename" ]; then
        echo "Table already exists!"
    else
        read -p "Enter columns (name:type), separated by commas: " columns
        echo "$columns" > "$tablename.meta"
        touch "$tablename"
        echo "Table created."
    fi
    database_menu
}

# List Tables
function list_tables() {
    echo "Tables:"
    ls | grep -v ".meta"
    database_menu
}

# Drop Table
function drop_table() {
    read -p "Enter table name to drop: " tablename
    if [ -f "$tablename" ]; then
        rm "$tablename" "$tablename.meta"
        echo "Table dropped."
    else
        echo "Table does not exist!"
    fi
    database_menu
}

# Insert Into Table
function insert_into_table() {
    read -p "Enter table name: " tablename
    if [ ! -f "$tablename" ]; then
        echo "Table does not exist!"
        database_menu
    fi

    columns=$(cat "$tablename.meta")
    IFS=',' read -ra col_arr <<< "$columns"
    values=()

    for col in "${col_arr[@]}"; do
        name=$(echo $col | cut -d':' -f1)
        type=$(echo $col | cut -d':' -f2)
        read -p "Enter value for $name ($type): " value
        # Basic datatype check
        if [[ "$type" == "int" && ! "$value" =~ ^[0-9]+$ ]]; then
            echo "Invalid value for $name. Expected integer."
            database_menu
        fi
        values+=($value)
    done
    echo "${values[@]}" | tr ' ' '|' >> "$tablename"
    echo "Row inserted."
    database_menu
}

# Select From Table
function select_from_table() {
    read -p "Enter table name: " tablename
    if [ ! -f "$tablename" ]; then
        echo "Table does not exist!"
    else
        cat "$tablename" | column -t -s '|'
    fi
    database_menu
}

# Delete From Table
function delete_from_table() {
    read -p "Enter table name: " tablename
    if [ ! -f "$tablename" ]; then
        echo "Table does not exist!"
    else
        read -p "Enter value to delete rows by: " value
        grep -v "$value" "$tablename" > tmp && mv tmp "$tablename"
        echo "Rows deleted."
    fi
    database_menu
}

# Update Table
function update_table() {
    read -p "Enter table name: " tablename
    if [ ! -f "$tablename" ]; then
        echo "Table does not exist!"
    else
        read -p "Enter search value: " search
        read -p "Enter column to update: " column
        read -p "Enter new value: " new_value

        col_index=$(awk -F'|' -v col="$column" 'NR==1{for(i=1;i<=NF;i++)if($i==col)print i}' "$tablename.meta")
        awk -F'|' -v search="$search" -v col=$col_index -v new_value="$new_value" '{if($col==search)$col=new_value; print}' "$tablename" > tmp && mv tmp "$tablename"
        echo "Rows updated."
    fi
    database_menu
}

main_menu
