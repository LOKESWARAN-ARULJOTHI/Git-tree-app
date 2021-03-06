import { useCallback, useState } from "react";
import axios from "axios";
import {
  FormControl,
  FormLabel,
  Input,
  Button,
  Box,
  Spinner,
  Flex,
  Code,
  Heading,
  Divider,
  Alert,
  AlertDescription,
  AlertIcon,
  AlertTitle,
  Text,
  Img,
} from "@chakra-ui/react";

function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [url, setUrl] = useState("");
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);
  const handleSubmit = useCallback(
    async (e) => {
      e.preventDefault();
      try {
        setLoading(true);
        const res = await axios.post(
          "/",
          { repourl: url, csrfmiddlewaretoken: getCookie("csrftoken") },
          {
            credentials: "include",
            method: "POST",
            mode: "same-origin",
            headers: {
              Accept: "application/json",
              "Content-Type": "application/json",
              "X-CSRFToken": getCookie("csrftoken"),
            },
          }
        );
        console.log(res);
        setError(null);
        setData(res.data);
        setLoading(false);
      } catch (err) {
        setLoading(false);
        setError("Please enter valid URL");
        console.log(err.message);
      }
    },
    [url]
  );
  const copyTree = async () => {
    try {
      if (copied) {
        return;
      }

      let treeText = data.reduce((acc, cur) => acc + `${cur}\n`, "```\n");
      treeText +=
        "```\n©generated by [GitTree](https://gittree.herokuapp.com/)\n";
      await navigator.clipboard.writeText(treeText);
      setTimeout(() => setCopied(false), 2000);
      setCopied(true);
    } catch (err) {
      console.log(err.message);
    }
  };
  return (
    <Flex align="center" justify="center">
      <Box maxWidth="600px" width="95vw">
        <Flex direction="column" align="center">
          <Heading
            fontSize={["5xl", "7xl"]}
            mt=".5rem"
            mb="1rem"
            color="blue.900"
            as="a"
            target="_blank"
            href="https://github.com/LOKESWARAN-ARULJOTHI/Git-tree-app"
            borderBottom="3px solid purple"
          >
            GitTree
          </Heading>

          <Box as="form" onSubmit={handleSubmit} mb="2rem" width="100%">
            <Input
              type="hidden"
              name="csrfmiddlewaretoken"
              value={getCookie("csrftoken")}
            />
            <FormControl id="email">
              <Flex
                direction={["column", "row"]}
                align={["stretch", "flex-end"]}
                justify={["flex-start", "space-between"]}
              >
                <Box width={["100%", "80%"]} mb={[".5rem", "0"]}>
                  <FormLabel color="blue.600">
                    Enter your Github Repository URL
                  </FormLabel>
                  <Input
                    type="url"
                    name="repourl"
                    id="repourl"
                    required
                    value={url}
                    placeholder="Eg: https://github.com/LOKESWARAN-ARULJOTHI/Git-tree-app"
                    onChange={(e) => setUrl(e.target.value)}
                  />
                </Box>
                <Button
                  _focus={{ outline: "none !important" }}
                  variant="solid"
                  type="submit"
                  bg="blue.900"
                  color="white"
                  _hover={{
                    bg: "blue.500",
                  }}
                  width={["100%", "15%"]}
                >
                  Get Tree
                </Button>
              </Flex>
            </FormControl>
          </Box>
        </Flex>

        <Code
          width="100%"
          p="1rem"
          pos="relative"
          height="63vh"
          overflowY="scroll"
          variant="solid"
          bg="blue.900"
        >
          {loading ? (
            <Flex justify="center" align="center">
              <Spinner size="xl" thickness="5px" color="white" />
            </Flex>
          ) : error ? (
            <Alert status="error" bg="blue.900">
              <AlertIcon color="white" />
              <AlertTitle mr={2} color="white">
                Error!
              </AlertTitle>
              <AlertDescription color="white">{error}</AlertDescription>
            </Alert>
          ) : data.length > 0 ? (
            <>
              <Button
                bg="whiteAlpha.900"
                pos="absolute"
                top="1rem"
                right="1rem"
                _hover={{
                  bg: "whiteAlpha.700",
                }}
                onClick={copyTree}
                variant="solid"
                color="white"
                _focus={{ outline: "none !important" }}
              >
                {copied ? (
                  <Text color="blue.900">Copied</Text>
                ) : (
                  <Img
                    width="1.4rem"
                    height="1.4rem"
                    alt="clipboard-icon"
                    src="https://img.icons8.com/fluency-systems-regular/48/1A365D/clipboard.png"
                  />
                )}
              </Button>
              {data.map((item) => (
                <pre>{item}</pre>
              ))}
              <br />© Generated by GitTree
            </>
          ) : null}
        </Code>
        <Divider my=".8rem" />
        <Text color="purple" textAlign="center">
          2021 &copy;{" "}
          <Text
            as="a"
            target="_blank"
            href="https://github.com/LOKESWARAN-ARULJOTHI/Git-tree-app"
          >
            GitTree
          </Text>
        </Text>
      </Box>
    </Flex>
  );
}
export default App;
