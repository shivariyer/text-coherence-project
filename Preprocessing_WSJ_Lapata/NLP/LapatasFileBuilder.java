package NLP;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class LapatasFileBuilder {
  public static Map<String, Integer> docId = new HashMap<>();
  
  public static void main(String[] args) {
    String path = "/Users/Sanaya/text-coherence-project/data/barzilay-lapata";
    try {
      BufferedReader br = new BufferedReader(new FileReader(new File(path + "/names_data1_train.txt")));
      String eachLine = "";
      while ((eachLine = br.readLine()) != null && eachLine.length() != 0) {
        if (! docId.containsKey(eachLine)) {
          docId.put(eachLine, 0);
        }
      }
      rewireFiles(path);
    } catch (IOException e) {
      // TODO Auto-generated catch block
      e.printStackTrace();
    }
  }
  
  public static void rewireFiles(String path) {
    path = path + "/data1/train-perm";
    File directory = new File(path);
    File[] files = directory.listFiles();
    String fileName;
    for (int i = 0; i < files.length; i++) {
      if (files[i].getName().contains(".perm-")) {
        fileName = files[i].getName().substring(0, 16);
        if (docId.containsKey(fileName)) {
          if (docId.get(fileName) <= 4) {
            docId.replace(fileName, docId.get(fileName), docId.get(fileName) + 1);
            reformThisFile(files[i], files[i].getName());
          }
        }
        //System.out.println(fileName);
      }
    }
  }
  
  public static void reformThisFile(File file, String fName) {
    try {
      BufferedReader br = new BufferedReader(new FileReader(file));
      String eachLine = "";
      List<String> fileContents = new ArrayList<>();
      //String[] fileContents = new String[2];
      while ((eachLine = br.readLine()) != null && eachLine.length() != 0) {
        fileContents.add(eachLine.split("\\s+", 2)[1]);//.add(eachLine.substring(20));
      }
      BufferedWriter bw =new BufferedWriter(new FileWriter(new File("/Users/Sanaya/Downloads/OutputLapata/" + fName + ".txt")));
      for (String line : fileContents) {
        bw.write(line + "\n" + "\n");
      }
      bw.flush();
    } catch (IOException e) {
      // TODO Auto-generated catch block
      e.printStackTrace();
    }
  }
}

