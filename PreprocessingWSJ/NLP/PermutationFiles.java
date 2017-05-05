package NLP;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.util.concurrent.ThreadLocalRandom;

public class PermutationFiles {
  
  public static void listToArray(List<String> allLines, int docNo, int permNo) {
    String[] toPass = new String[allLines.size()];
    for (int i = 0; i < allLines.size(); i++) {
      toPass[i] = allLines.get(i);
      //System.out.println("here: " + toPass[i]);
    }
    shuffleArray(toPass);
    String path = "/Users/Sanaya/Downloads/Output/doc_";
    BufferedWriter bw;
    try {
      bw = new BufferedWriter(new FileWriter(new File(path + docNo + ".perm-" + permNo + ".txt")));
      for (int i = 0; i < toPass.length; i++)
      {
        System.out.print(toPass[i] + " ");
        bw.write(toPass[i] + "\n" + "\n");
        bw.flush();
      }
    } catch (IOException e) {
      // TODO Auto-generated catch block
      e.printStackTrace();
    }
    
    for (int i = 0; i < toPass.length; i++)
    {
      System.out.print(toPass[i] + " ");
    }
    System.out.println();
  }
  
  /*public static void main(String args[])
  {
    List<String> lis = new ArrayList<>();
    lis.add("This");
    lis.add("is");
    lis.add("just");
    lis.add("a");
    lis.add("test");
    listToArray(lis, 1);
  }*/

  // Implementing Fisher–Yates shuffle
  static void shuffleArray(String[] ar)
  {
    // If running on Java 6 or older, use `new Random()` on RHS here
    Random rnd = ThreadLocalRandom.current();
    for (int i = ar.length - 1; i > 0; i--)
    {
      int index = rnd.nextInt(i + 1);
      // Simple swap
      String a = ar[index];
      ar[index] = ar[i];
      ar[i] = a;
    }
  }
}
