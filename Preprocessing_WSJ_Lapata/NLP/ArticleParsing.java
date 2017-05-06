package NLP;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class ArticleParsing {
  private static List<List<String>> allArticles = new ArrayList<>();
  private static int articleStartFlag = 0;
  private static int currentArticleNumber = 0;
  
  public static void main(String[] args) {
    String path = "/Users/Sanaya/Downloads/94/ws94_0";
    String eachPath = "";
    for (int i = 1; i <= 47; i++) {
      if (i <= 9) {
        eachPath = path + "0" + i;
      }
      else {
        eachPath = path + i;
      }
      parseThem(eachPath);
    }
    
    try {
      BufferedWriter bw;
      File file;
      int dummy = 0;
      for (int index  = 0; index < allArticles.size(); index++) {
/*      int index = 0;
      while (dummy == 0) {
        dummy = 1;*/
        file = new File("/Users/Sanaya/Downloads/Output/doc_" + (index + 1) + ".txt");
        bw = new BufferedWriter(new FileWriter(file));
        for (int lines = 0; lines < allArticles.get(index).size(); lines++) {
          bw.write(allArticles.get(index).get(lines) + "\n" + "\n");
        }
        //System.out.println("file: " + allArticles.get(index));
        PermutationFiles.listToArray(allArticles.get(index), (index + 1), 1);
        PermutationFiles.listToArray(allArticles.get(index), (index + 1), 2);
        PermutationFiles.listToArray(allArticles.get(index), (index + 1), 3);
        bw.flush();
      }
      System.out.println("Number of articles detected: "+allArticles.size());
    } catch (IOException e) {
      // TODO Auto-generated catch block
      e.printStackTrace();
    }   
  }
  
  public static int parseThem(String path) {
    try {
      BufferedReader br = new BufferedReader(new FileReader(new File(path)));
      String line;
      String[] allWords;
      List<String> eachArticle = new ArrayList<>();
      while((line = br.readLine())!= null && line.length() != 0){
        allWords = line.split("\\s+");
        if (allWords.length == 1) {
          if (allWords[0].length() >= 5) {
            if (allWords[0].substring(0, 5).equals("<art.")) {
              if (articleStartFlag == 0) {
                articleStartFlag = 1;
                currentArticleNumber += 1;
                eachArticle = new ArrayList<>();
              }
            }
            else if (allWords[0].length() == 6 && allWords[0].substring(0, 6).equals("</art>")) {
              allArticles.add(eachArticle);
              articleStartFlag = 0;
            }
          }
        }
        else {
          eachArticle.add(line);
        }         
      }
    }
    catch (IOException e) {
      // TODO Auto-generated catch block
      e.printStackTrace();
    }
    return allArticles.size();
  }
}
