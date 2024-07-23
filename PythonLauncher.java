import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class PythonLauncher {
    public static void main(String[] args) throws InterruptedException {
        String arg = "C:\\Users\\jianx\\PycharmProjects\\pythonProject\\dicomFolder"; //TODO 替换为当前使用的DICOM目录

        String scriptPath = "C:\\Users\\jianx\\PycharmProjects\\pythonProject\\server_8765.py"; //TODO 替换为脚本的项目下相对路径
        ProcessBuilder processBuilder = new ProcessBuilder("python", scriptPath, arg);
        processBuilder.redirectErrorStream(true); // Python脚本的输出放进Java输出流里

        try {
            Process process = processBuilder.start();
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));

            String line;
            while ((line = reader.readLine()) != null) {
                System.out.println(line); // Python脚本的输出放进Java输出流里
            }

            int exitCode = process.waitFor();
            System.out.println("Exited with error code : " + exitCode);

            //TODO 删掉sleep，并把process.destroy();放到真正想要结束脚本的地方
            Thread.sleep(10000);
            process.destroy();

        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
    }
}