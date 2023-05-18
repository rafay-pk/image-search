using System;
using System.Collections.Generic;
using System.Data;
using System.IO;
using System.Linq;
using System.Text;
using Mono.Data.Sqlite;
using UnityEngine;

namespace Mechanics
{
    public class Data : Singleton<Data>
    {
        #region Setup
        private IDbConnection sqlite;

        protected override void BootOrderAwake()
        {
            print(Application.persistentDataPath);
            sqlite = new SqliteConnection("URI=file:" + Application.persistentDataPath + "/db.sql");
            NonQuery(File.ReadAllText(Application.streamingAssetsPath + "/create.sql"));
            base.BootOrderAwake();
        }
        #endregion
        
        #region Private Methods
        private void NonQuery(string arg_sql)
        {
            sqlite.Open();
            var _command = sqlite.CreateCommand();
            _command.CommandText = arg_sql;
            try
            {
                _command.ExecuteNonQuery();
            }
            finally
            {
                sqlite.Close();
            }
        }
        #endregion
        
        #region Unity API
        public void AddNewTag(string arg_tag)
        {
            NonQuery($"INSERT INTO Tags (name) VALUES ('{arg_tag}')");
        }
        public void AddFile(string arg_file)
        {
            NonQuery($"INSERT INTO Files (path) VALUES ('{arg_file}')");
        }
        public void AddTagToFile(string arg_tag, string arg_file)
        {
            NonQuery(@$"INSERT OR IGNORE INTO Tags (name) VALUES ('{arg_tag}');
            INSERT INTO FileTags (file_id, tag_id) VALUES 
            (
	            (SELECT id FROM Files WHERE path = '{arg_file}'),
	            (SELECT id FROM Tags WHERE name = '{arg_tag}')
            );");
        }
        public string[] GetAllFiles()
        {
            var _list = new List<string>();
            sqlite.Open();
            var _command = sqlite.CreateCommand();
            _command.CommandText = "SELECT * FROM Files";
            try
            {
                var _reader = _command.ExecuteReader();
                while (_reader.Read())
                {
                    _list.Add(_reader.GetString(1));
                }
            }
            catch (Exception e)
            {
                print(e.Message);
            }
            finally
            {
                sqlite.Close();
            }
            return _list.ToArray();
        }
        public string[] GetFileTags(string arg_file)
        {
            var _list = new List<string>();
            sqlite.Open();
            var _command = sqlite.CreateCommand();
            _command.CommandText = "SELECT t.name FROM FileTags ft JOIN Files f ON ft.file_id = f.id JOIN Tags t ON ft.tag_id = t.id WHERE f.path = \"" + arg_file + "\"";
            try
            {
                var _reader = _command.ExecuteReader();
                while (_reader.Read())
                {
                    _list.Add(_reader.GetString(0));
                }
            }
            finally
            {
                sqlite.Close();
            }
            return _list.ToArray();
        }
        public string[] Search(string[] arg_tags)
        {
            var _list = new List<string>();
            sqlite.Open();
            var _command = sqlite.CreateCommand();
            var _string = new StringBuilder()
                .Append(@$"SELECT DISTINCT f.path FROM FileTags ft JOIN Files f ON
                        ft.file_id = f.id JOIN Tags t ON ft.tag_id = t.id WHERE 
                        t.name = '{arg_tags[0]}'");
            for (var i = 1; i < arg_tags.Length; i++)
            {
                _string.Append($" OR t.name = '{arg_tags[i]}'");
            }
            _command.CommandText = _string.ToString();
            print(_command.CommandText);
            var _reader = _command.ExecuteReader();
            while (_reader.Read())
            {
                _list.Add(_reader.GetString(0));
            }
            sqlite.Close();
            return _list.ToArray();
        }
        public void EditTag(string arg_current, string arg_new)
        {
            
        }
        public void RemoveTag(string arg_tag)
        {
            
        }
        public void RemoveTagFromFile(string arg_tag, string arg_file)
        {
            
        }
        #endregion
    }
}