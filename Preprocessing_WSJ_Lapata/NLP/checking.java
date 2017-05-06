package NLP;

import java.io.File;

public class checking {
  public static void main(String[] args) {
    String path = "/Users/Sanaya/Downloads/OutputLapata";
    File dir = new File(path);
    File[] f = dir.listFiles();
    int c = 0;
    for (int i = 0; i < f.length; i++) {
      if (f[i].getName().contains(".perm-1.txt")) {
        c += 1;
      }
    }
    System.out.println("count: " + c);
  }
}
